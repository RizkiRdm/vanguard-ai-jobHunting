import type { Page } from 'playwright';
import { generateJson } from '../ai/gemini.ts';
import { AiDecision, AGENT_SYSTEM_PROMPT } from '../ai/prompts.ts';
import { logger } from '../../lib/logger.ts';

export type ApplicationOutcome =
  | { kind: 'awaiting_approval'; submitSelector: string; reason: string }
  | { kind: 'awaiting_input'; reason: string }
  | { kind: 'submitted' }
  | { kind: 'failed'; reason: string };

export interface ApplicationContext {
  page: Page;
  userId: string;
  url: string;
  goal: string;
  resume: { name: string; buffer: Buffer } | null;
  /** True when the user has already confirmed this specific submission. */
  approved: boolean;
  /** Selector captured when approval was requested. */
  submitSelector?: string | null;
  maxSteps?: number;
}

interface HistoryEntry {
  step: number;
  action: string;
  selector?: string;
  thought?: string;
}

const MAX_STEPS = 12;

/**
 * Fills a job application form.
 *
 * The agent never submits on its own: when the form is ready it returns
 * `awaiting_approval` and the task is parked until the user confirms. Only a
 * task that was explicitly approved (and carries the captured submit selector)
 * reaches the actual submit click.
 */
export async function runApplication(ctx: ApplicationContext): Promise<ApplicationOutcome> {
  const maxSteps = ctx.maxSteps ?? MAX_STEPS;
  const history: HistoryEntry[] = [];

  try {
    await ctx.page.goto(ctx.url, { waitUntil: 'domcontentloaded' });
  } catch (error) {
    return {
      kind: 'failed',
      reason: `Could not open the job page: ${error instanceof Error ? error.message : 'unknown error'}`,
    };
  }

  if (ctx.approved && ctx.submitSelector) {
    try {
      await ctx.page.click(ctx.submitSelector, { timeout: 15_000 });
      return { kind: 'submitted' };
    } catch (error) {
      return {
        kind: 'failed',
        reason: `Approved submission failed: ${error instanceof Error ? error.message : 'unknown error'}`,
      };
    }
  }

  for (let step = 0; step < maxSteps; step += 1) {
    const screenshot = await ctx.page.screenshot({ type: 'png' });

    const prompt = [
      `Goal: ${ctx.goal}`,
      `Step: ${step + 1} of ${maxSteps}`,
      `Recent actions: ${JSON.stringify(history.slice(-5))}`,
      'What is the next action?',
    ].join('\n');

    let decision: AiDecision;
    try {
      decision = await generateJson({
        prompt,
        userId: ctx.userId,
        schema: AiDecision,
        imageBase64: screenshot.toString('base64'),
        system: AGENT_SYSTEM_PROMPT,
      });
    } catch (error) {
      return {
        kind: 'failed',
        reason: error instanceof Error ? error.message : 'AI decision failed',
      };
    }

    logger.info('ai_decision', {
      userId: ctx.userId,
      step,
      action: decision.action,
      selector: decision.selector,
    });

    history.push({
      step,
      action: decision.action,
      selector: decision.selector,
      thought: decision.thought,
    });

    try {
      switch (decision.action) {
        case 'click':
          await ctx.page.click(decision.selector ?? '', { timeout: 10_000 });
          break;
        case 'fill':
          await ctx.page.fill(decision.selector ?? '', decision.value ?? '', { timeout: 10_000 });
          break;
        case 'select':
          await ctx.page.selectOption(decision.selector ?? '', decision.value ?? '', {
            timeout: 10_000,
          });
          break;
        case 'upload': {
          if (!ctx.resume) {
            return { kind: 'failed', reason: 'The form asks for a resume but none is uploaded.' };
          }
          await ctx.page.setInputFiles(decision.selector ?? '', {
            name: ctx.resume.name,
            mimeType: 'application/pdf',
            buffer: ctx.resume.buffer,
          });
          break;
        }
        case 'ready_to_submit': {
          if (!decision.selector) {
            return {
              kind: 'failed',
              reason: 'AI reported the form was ready but gave no submit button.',
            };
          }
          return {
            kind: 'awaiting_approval',
            submitSelector: decision.selector,
            reason: decision.thought ?? 'The application form is filled and ready to submit.',
          };
        }
        case 'await_user':
          return {
            kind: 'awaiting_input',
            reason: decision.reason ?? decision.thought ?? 'More information is needed.',
          };
        case 'fail':
          return { kind: 'failed', reason: decision.reason ?? 'The agent stopped.' };
      }
    } catch (error) {
      return {
        kind: 'failed',
        reason: `Action "${decision.action}" failed: ${error instanceof Error ? error.message : 'unknown error'}`,
      };
    }
  }

  return { kind: 'failed', reason: 'Maximum number of steps reached.' };
}
