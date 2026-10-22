import type { Task } from '@vanguard/contracts';
import { sql } from 'drizzle-orm';
import { getEnv } from '../../config/env.ts';
import { getDrizzle } from '../../lib/db.ts';
import { logger } from '../../lib/logger.ts';
import { getAdminClient } from '../../lib/supabase.ts';
import { openSession } from '../../infrastructure/browser/session.ts';
import { searchJobs } from '../../infrastructure/browser/discovery.ts';
import { runApplication } from '../../infrastructure/browser/application.ts';
import { insertJob } from '../jobs/repository.ts';
import { getProfile } from '../profile/repository.ts';
import * as repo from './repository.ts';

const log = logger.child({ service: 'task_worker' });

async function requestApproval(
  task: Task,
  workerId: string,
  reason: string,
  details: Record<string, unknown>,
): Promise<void> {
  await getDrizzle().execute(
    sql`select public.request_approval(
      ${task.id},
      ${workerId},
      ${reason},
      ${JSON.stringify(details)}::jsonb
    )`,
  );
}

async function retryOrFail(task: Task, workerId: string, error: string): Promise<void> {
  const backoff = Math.min(60, 5 * task.attempts);
  await getDrizzle().execute(
    sql`select public.retry_task(${task.id}, ${workerId}, ${error}, ${backoff})`,
  );
}

async function downloadResume(
  resumePath: string,
): Promise<{ name: string; buffer: Buffer } | null> {
  const { data, error } = await getAdminClient().storage.from('resumes').download(resumePath);
  if (error || !data) {
    log.warn('resume_download_failed', { resumePath, error: error?.message });
    return null;
  }
  return {
    name: resumePath.split('/').pop() ?? 'resume.pdf',
    buffer: Buffer.from(await data.arrayBuffer()),
  };
}

async function runDiscovery(task: Task): Promise<void> {
  const query = String(task.payload.query ?? '');
  const limit = Number(task.payload.limit ?? 20);
  if (!query) throw new Error('Discovery task has no query');

  const session = await openSession(task.user_id);
  try {
    const candidates = await searchJobs(session.page, query, limit);
    for (const candidate of candidates) {
      await insertJob({
        userId: task.user_id,
        taskId: task.id,
        sourceUrl: candidate.url,
        title: candidate.title,
        company: candidate.company,
        location: candidate.location,
        description: candidate.snippet,
      });
    }
    log.info('discovery_finished', { taskId: task.id, found: candidates.length });
  } finally {
    await session.close();
  }
}

async function runApplicationTask(task: Task, workerId: string): Promise<void> {
  const url = String(task.payload.source_url ?? '');
  if (!url) throw new Error('Apply task has no source_url');

  const profile = await getProfile(task.user_id);
  const approved = Boolean(task.approval && 'approved_at' in task.approval);
  const submitSelector =
    typeof task.approval?.details?.submit_selector === 'string'
      ? task.approval.details.submit_selector
      : null;

  const userAnswer =
    typeof task.payload.user_answer === 'object' && task.payload.user_answer !== null
      ? JSON.stringify(task.payload.user_answer)
      : '';

  const goal = [
    `Fill and submit the job application for "${task.payload.title ?? 'the job'}"`,
    `Candidate: ${profile?.full_name ?? 'unknown'}`,
    `Target role: ${profile?.target_role ?? 'unknown'}`,
    `Summary: ${profile?.summary ?? 'not provided'}`,
    `Expected salary: ${profile?.expected_salary ?? 'not provided'}`,
    userAnswer ? `Answers supplied by the user: ${userAnswer}` : '',
  ]
    .filter(Boolean)
    .join('\n');

  const resume = profile?.resume_path ? await downloadResume(profile.resume_path) : null;

  const session = await openSession(task.user_id);
  try {
    const outcome = await runApplication({
      page: session.page,
      userId: task.user_id,
      url,
      goal,
      resume,
      approved,
      submitSelector,
    });

    if (outcome.kind === 'awaiting_approval') {
      await requestApproval(task, workerId, outcome.reason, {
        kind: 'approval',
        submit_selector: outcome.submitSelector,
        job: { title: task.payload.title ?? null, company: task.payload.company ?? null, url },
      });
      log.info('task_awaiting_approval', { taskId: task.id });
      return;
    }

    if (outcome.kind === 'awaiting_input') {
      await requestApproval(task, workerId, outcome.reason, { kind: 'input' });
      log.info('task_awaiting_input', { taskId: task.id });
      return;
    }

    if (outcome.kind === 'submitted') {
      await repo.finishTask({
        taskId: task.id,
        workerId,
        status: 'succeeded',
        result: { submitted_at: new Date().toISOString(), url },
      });
      log.info('application_submitted', { taskId: task.id });
      return;
    }

    throw new Error(outcome.reason);
  } finally {
    await session.close();
  }
}

export class TaskWorker {
  private readonly workerId: string;
  private readonly concurrency: number;
  private readonly pollMs: number;
  private readonly leaseSeconds: number;
  private readonly inFlight = new Set<Promise<void>>();
  private stopping = false;

  constructor(workerId = `worker-${process.pid}`) {
    const env = getEnv();
    this.workerId = workerId;
    this.concurrency = env.WORKER_CONCURRENCY;
    this.pollMs = env.WORKER_POLL_MS;
    this.leaseSeconds = env.TASK_LEASE_SECONDS;
  }

  async run(): Promise<void> {
    log.info('worker_started', {
      workerId: this.workerId,
      concurrency: this.concurrency,
      provider: 'postgres_task_queue',
    });

    let active = 0;
    let lastReclaim = 0;

    while (!this.stopping) {
      if (active >= this.concurrency) {
        await this.sleep(200);
        continue;
      }

      if (Date.now() - lastReclaim > 60_000) {
        lastReclaim = Date.now();
        const reclaimed = await repo.reclaimExpiredTasks().catch(() => 0);
        if (reclaimed > 0) log.warn('tasks_reclaimed', { count: reclaimed });
      }

      const task = await repo.claimNextTask(this.workerId, this.leaseSeconds).catch((err) => {
        log.error('claim_failed', { error: err instanceof Error ? err.message : String(err) });
        return null;
      });

      if (!task) {
        await this.sleep(this.pollMs);
        continue;
      }

      active += 1;
      const running = this.execute(task).finally(() => {
        active -= 1;
        this.inFlight.delete(running);
      });
      this.inFlight.add(running);
    }

    // Graceful shutdown: let claimed tasks settle before the process closes the pool,
    // so we do not strand a half-written application mid-run.
    if (this.inFlight.size > 0) {
      log.info('worker_draining', { tasks: this.inFlight.size });
      await Promise.allSettled([...this.inFlight]);
    }

    log.info('worker_stopped', { workerId: this.workerId });
  }

  stop(): void {
    this.stopping = true;
  }

  private async execute(task: Task): Promise<void> {
    const log2 = log.child({ taskId: task.id, userId: task.user_id, type: task.type });
    const heartbeat = setInterval(
      () => {
        void repo.heartbeatTask(task.id, this.workerId, this.leaseSeconds).catch(() => undefined);
      },
      Math.max(5000, Math.floor((this.leaseSeconds * 1000) / 3)),
    );

    try {
      if (task.type === 'discover') {
        await runDiscovery(task);
        await repo.finishTask({ taskId: task.id, workerId: this.workerId, status: 'succeeded' });
      } else if (task.type === 'apply') {
        await runApplicationTask(task, this.workerId);
      } else {
        throw new Error(`Unsupported task type: ${task.type}`);
      }
      log2.info('task_finished');
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      log2.error('task_failed', { error: message });
      await retryOrFail(task, this.workerId, message).catch(() => undefined);
    } finally {
      clearInterval(heartbeat);
    }
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
