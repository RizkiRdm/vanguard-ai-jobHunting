<script lang="ts">
  import { invalidateAll } from '$app/navigation';
  import StatusBadge from '../../lib/components/StatusBadge.svelte';

  let { data, form } = $props();

  const tasks = $derived(data.tasks);
  const jobs = $derived(data.jobs ?? []);
  const jobsError = $derived(data.jobsError);
  const running = $derived(tasks.some((t) => t.status === 'running' || t.status === 'queued'));
  const waitingTasks = $derived(tasks.filter((t) => t.status === 'waiting_for_user'));
</script>

{#if form?.error}
  <div class="alert alert-error text-sm py-2 px-3 mb-4 rounded-lg border border-[var(--coral)] bg-red-950/40 text-red-200" role="alert">
    <span>{form.error}</span>
  </div>
{/if}
{#if form?.created}
  <div class="alert alert-success text-sm py-2 px-3 mb-4 rounded-lg border border-[var(--mint)] bg-emerald-950/40 text-emerald-200" role="status">
    <span>Task created. <a href="/tasks/{form.created}" class="underline font-medium">Open task {form.created}</a>.</span>
  </div>
{/if}

<!-- Issue #92: Human-in-the-loop attention banner -->
{#if waitingTasks.length > 0}
  <aside
    class="alert border-2 border-[var(--amber)] bg-[#2b2111] text-[var(--snow)] rounded-xl p-4 mb-6 shadow-lg flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
    role="alert"
    aria-label="Pending user action"
  >
    <div class="flex items-center gap-3">
      <span class="inline-flex items-center justify-center h-8 w-8 rounded-full bg-[var(--amber)] text-black font-bold">
        !
      </span>
      <div>
        <h3 class="font-semibold text-base text-[var(--amber)]">
          {waitingTasks.length} {waitingTasks.length === 1 ? 'task requires' : 'tasks require'} your input
        </h3>
        <p class="text-xs text-[var(--chalk)]">
          Vanguard paused to prevent unintended action. Please answer or approve to resume.
        </p>
      </div>
    </div>
    <div class="flex items-center gap-2">
      {#each waitingTasks as waitingTask (waitingTask.id)}
        <a class="btn btn-sm bg-[var(--amber)] text-black hover:bg-amber-400 border-none font-medium" href="/tasks/{waitingTask.id}">
          Review Task {waitingTask.id.slice(0, 8)}
        </a>
      {/each}
    </div>
  </aside>
{/if}

<div class="dashboard-layout grid grid-cols-1 lg:grid-cols-3 gap-6">
  <section class="panel lg:col-span-2 bg-[var(--graphite)] border border-[var(--hairline)] rounded-xl p-5">
    <div class="panel-header flex items-center justify-between pb-4 border-b border-[var(--hairline)] mb-4">
      <h2 class="panel-title text-lg font-medium text-[var(--snow)]">Tasks</h2>
      <div class="btn-row flex items-center gap-3">
        <button class="btn btn-secondary btn-small text-xs py-1 px-3 rounded-lg border border-[var(--hairline)] hover:bg-[var(--smoke)] text-[var(--snow)]" onclick={() => invalidateAll()}>Refresh</button>
        {#if running}
          <span class="muted micro text-xs text-[var(--steel)]">Work in progress — open a task to follow it.</span>
        {/if}
      </div>
    </div>

    {#if tasks.length === 0}
      <p class="empty-state text-sm text-[var(--fog)] py-6 text-center">No tasks yet. Start a discovery run to find real job postings.</p>
    {:else}
      <ul class="task-list space-y-3">
        {#each tasks as task (task.id)}
          <li class="task-card p-3 rounded-lg bg-[var(--charcoal)] border border-[var(--hairline)] hover:border-[var(--steel)] transition-colors">
            <div class="task-card-main flex items-center justify-between gap-4">
              <div class="task-summary flex-1 min-w-0">
                <div class="task-summary-top flex items-center gap-2 mb-1">
                  <span class="task-title font-medium text-sm text-[var(--snow)]">{task.type}</span>
                  <StatusBadge status={task.status} />
                </div>
                <div class="task-meta flex items-center gap-2 text-xs text-[var(--steel)]">
                  <span class="task-id font-mono text-[11px]">{task.id}</span>
                  <span>·</span>
                  <span class="muted micro">{new Date(task.created_at).toLocaleString()}</span>
                </div>
              </div>
              <a class="btn btn-quiet btn-small text-xs py-1 px-3 rounded border border-[var(--hairline)] hover:bg-[var(--smoke)] text-[var(--snow)] shrink-0" href="/tasks/{task.id}">Open</a>
            </div>
          </li>
        {/each}
      </ul>
    {/if}
  </section>

  <div class="dashboard-side space-y-6">
    <section class="panel bg-[var(--graphite)] border border-[var(--hairline)] rounded-xl p-5">
      <h2 class="panel-title text-base font-medium text-[var(--snow)] mb-1">Find jobs</h2>
      <p class="panel-description text-xs text-[var(--fog)] mb-4">
        Searches the live web and stores only listings it actually saw.
      </p>
      <form method="POST" action="?/discover" class="space-y-4">
        <div class="form-control w-full">
          <label class="label py-1" for="query">
            <span class="label-text text-xs text-[var(--chalk)]">Search query</span>
          </label>
          <input
            id="query"
            name="query"
            required
            minlength="2"
            maxlength="200"
            placeholder="backend engineer remote"
            class="input input-bordered w-full text-sm bg-[var(--charcoal)] border-[var(--hairline)] text-[var(--snow)] focus:border-[var(--arc-blue)] focus:ring-1 focus:ring-[var(--ring-blue)]"
          />
        </div>
        <div class="form-control w-full">
          <label class="label py-1" for="limit">
            <span class="label-text text-xs text-[var(--chalk)]">Max results</span>
          </label>
          <input
            id="limit"
            name="limit"
            type="number"
            min="1"
            max="50"
            value="20"
            class="input input-bordered w-full text-sm bg-[var(--charcoal)] border-[var(--hairline)] text-[var(--snow)] focus:border-[var(--arc-blue)] focus:ring-1 focus:ring-[var(--ring-blue)]"
          />
        </div>
        <div class="pt-1">
          <button class="btn btn-primary w-full bg-[var(--bone)] text-[var(--ink)] hover:bg-white border-none font-medium text-sm h-10" type="submit">
            Start discovery
          </button>
        </div>
      </form>
    </section>

    <section class="panel bg-[var(--graphite)] border border-[var(--hairline)] rounded-xl p-5">
      <h2 class="panel-title text-base font-medium text-[var(--snow)] mb-1">Apply to a job URL</h2>
      <p class="panel-description text-xs text-[var(--fog)] mb-4">
        Vanguard fills the form and stops before submitting. You approve every submission.
      </p>
      <form method="POST" action="?/apply" class="space-y-4">
        <div class="form-control w-full">
          <label class="label py-1" for="source_url">
            <span class="label-text text-xs text-[var(--chalk)]">Job posting URL</span>
          </label>
          <input
            id="source_url"
            name="source_url"
            type="url"
            required
            placeholder="https://…"
            class="input input-bordered w-full text-sm bg-[var(--charcoal)] border-[var(--hairline)] text-[var(--snow)] focus:border-[var(--arc-blue)] focus:ring-1 focus:ring-[var(--ring-blue)]"
          />
        </div>
        <div class="form-control w-full">
          <label class="label py-1" for="title">
            <span class="label-text text-xs text-[var(--chalk)]">Job title (optional)</span>
          </label>
          <input
            id="title"
            name="title"
            maxlength="200"
            class="input input-bordered w-full text-sm bg-[var(--charcoal)] border-[var(--hairline)] text-[var(--snow)] focus:border-[var(--arc-blue)] focus:ring-1 focus:ring-[var(--ring-blue)]"
          />
        </div>
        <div class="form-control w-full">
          <label class="label py-1" for="company">
            <span class="label-text text-xs text-[var(--chalk)]">Company (optional)</span>
          </label>
          <input
            id="company"
            name="company"
            maxlength="200"
            class="input input-bordered w-full text-sm bg-[var(--charcoal)] border-[var(--hairline)] text-[var(--snow)] focus:border-[var(--arc-blue)] focus:ring-1 focus:ring-[var(--ring-blue)]"
          />
        </div>
        <div class="pt-1">
          <button class="btn btn-primary w-full bg-[var(--bone)] text-[var(--ink)] hover:bg-white border-none font-medium text-sm h-10" type="submit">
            Prepare application
          </button>
        </div>
      </form>
    </section>

    <section class="panel bg-[var(--graphite)] border border-[var(--hairline)] rounded-xl p-5">
      <h2 class="panel-title text-base font-medium text-[var(--snow)] mb-3">Recent listings</h2>
      {#if jobsError}
        <div class="alert alert-error text-xs py-2 px-3 rounded-lg border border-[var(--coral)] bg-red-950/40 text-red-200" role="alert">
          <span>{jobsError}</span>
        </div>
      {:else if jobs.length === 0}
        <p class="empty-state text-xs text-[var(--fog)] py-4 text-center">No listings yet. Run a discovery task to populate this list.</p>
      {:else}
        <ul class="listing-list space-y-3">
          {#each jobs as job (job.id)}
            <li class="listing-card p-3 rounded-lg bg-[var(--charcoal)] border border-[var(--hairline)]">
              <a href={job.source_url} rel="noreferrer noopener" target="_blank" class="font-medium text-sm text-[var(--arc-blue)] hover:underline block truncate">
                {job.title}
              </a>
              <div class="muted micro text-xs text-[var(--steel)] mt-0.5">
                {job.company ?? 'Unknown company'}{job.location ? ` · ${job.location}` : ''}
              </div>
              {#if job.description}
                <p class="muted micro text-xs text-[var(--fog)] mt-1 line-clamp-2">{job.description}</p>
              {/if}
            </li>
          {/each}
        </ul>
      {/if}
    </section>
  </div>
</div>
