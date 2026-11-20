<script lang="ts">
  import { enhance } from '$app/forms';
  import { invalidateAll } from '$app/navigation';
  import StatusBadge from '../../../lib/components/StatusBadge.svelte';

  let { data, form } = $props();

  const task = $derived(data.task);
  const approval = $derived(task.approval);
  const wantsInput = $derived(approval?.details?.kind === 'input');
  const live = $derived(
    task.status === 'queued' || task.status === 'running' || task.status === 'waiting_for_user',
  );

  let isSubmitting = $state(false);

  $effect(() => {
    if (!live) return;
    const id = setInterval(() => void invalidateAll(), 3000);
    return () => clearInterval(id);
  });

  function confirmCancel(event: SubmitEvent) {
    if (!confirm('Are you sure you want to cancel this task?')) {
      event.preventDefault();
    }
  }
</script>

<div class="max-w-4xl mx-auto space-y-6">
  <!-- Navigation / Breadcrumbs -->
  <nav class="flex items-center gap-2 text-xs text-[var(--fog)]">
    <a
      href="/dashboard"
      class="text-[var(--arc-blue)] hover:underline inline-flex items-center gap-1 font-medium"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-3.5 w-3.5"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      Back to Dashboard
    </a>
    <span>/</span>
    <span class="text-[var(--chalk)]">Task {task.id.slice(0, 8)}</span>
  </nav>

  <!-- Status / Action Notifications -->
  {#if form?.error}
    <div
      class="alert alert-error text-sm py-3 px-4 rounded-xl border border-[var(--coral)] bg-red-950/40 text-red-200 shadow-sm"
      role="alert"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-5 w-5 shrink-0 stroke-current"
        fill="none"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <span>{form.error}</span>
    </div>
  {:else if form?.answered}
    <div
      class="alert alert-success text-sm py-3 px-4 rounded-xl border border-[var(--mint)] bg-emerald-950/40 text-emerald-200 shadow-sm"
      role="status"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-5 w-5 shrink-0 stroke-current"
        fill="none"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <span>Answer recorded! Resuming automated task execution...</span>
    </div>
  {:else if form?.approved}
    <div
      class="alert alert-success text-sm py-3 px-4 rounded-xl border border-[var(--mint)] bg-emerald-950/40 text-emerald-200 shadow-sm"
      role="status"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-5 w-5 shrink-0 stroke-current"
        fill="none"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <span>Application approved! Submitting application now...</span>
    </div>
  {:else if form?.cancelled}
    <div
      class="alert text-sm py-3 px-4 rounded-xl border border-[var(--hairline)] bg-[var(--charcoal)] text-[var(--chalk)] shadow-sm"
      role="status"
    >
      <span>Task cancelled.</span>
    </div>
  {/if}

  <!-- Task Overview Card -->
  <section
    class="bg-[var(--graphite)] border border-[var(--hairline)] rounded-2xl p-5 md:p-6 shadow-sm space-y-4"
  >
    <div
      class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[var(--hairline)] pb-4"
    >
      <div>
        <div class="flex items-center gap-2.5 flex-wrap">
          <h1 class="text-xl font-bold tracking-tight text-[var(--snow)] capitalize">
            {task.type} Task
          </h1>
          <StatusBadge status={task.status} />
          {#if live}
            <span
              class="inline-flex items-center gap-1.5 text-[11px] text-[var(--mint)] bg-emerald-950/40 border border-emerald-800/40 px-2 py-0.5 rounded-full font-medium"
            >
              <span class="h-1.5 w-1.5 rounded-full bg-[var(--mint)] animate-pulse"></span>
              Live auto-sync
            </span>
          {/if}
        </div>
        <p class="text-xs text-[var(--steel)] font-mono mt-1">
          ID: {task.id}
        </p>
      </div>

      {#if live}
        <form method="POST" action="?/cancel" onsubmit={confirmCancel}>
          <button
            class="btn btn-ghost btn-sm text-xs text-[var(--coral)] hover:bg-red-950/30 rounded-xl border border-red-900/30"
            type="submit"
          >
            Cancel Task
          </button>
        </form>
      {/if}
    </div>

    <!-- Metadata Grid -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
      <div class="space-y-0.5">
        <span class="text-[var(--fog)]">Created</span>
        <p class="font-medium text-[var(--snow)]">
          {new Date(task.created_at).toLocaleTimeString()}
        </p>
        <p class="text-[11px] text-[var(--steel)]">
          {new Date(task.created_at).toLocaleDateString()}
        </p>
      </div>
      <div class="space-y-0.5">
        <span class="text-[var(--fog)]">Attempts</span>
        <p class="font-medium text-[var(--snow)]">{task.attempts} / {task.max_attempts}</p>
      </div>
      <div class="space-y-0.5">
        <span class="text-[var(--fog)]">Last Updated</span>
        <p class="font-medium text-[var(--snow)]">
          {new Date(task.updated_at).toLocaleTimeString()}
        </p>
      </div>
      <div class="space-y-0.5">
        <span class="text-[var(--fog)]">Status</span>
        <p class="font-medium text-[var(--snow)] capitalize">{task.status.replace(/_/g, ' ')}</p>
      </div>
    </div>

    {#if task.status === 'failed' && task.error}
      <div
        class="p-4 rounded-xl bg-red-950/30 border border-red-900/40 text-xs text-red-200 space-y-1"
      >
        <div class="font-semibold flex items-center gap-1.5 text-[var(--coral)]">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          Failure Reason
        </div>
        <p class="font-mono">{task.error}</p>
      </div>
    {/if}
  </section>

  <!-- Issue #92: Human-in-the-loop (HITL) Action Card -->
  {#if task.status === 'waiting_for_user' && approval}
    <section
      class="border-2 border-[var(--amber)] bg-[#1e170a] rounded-2xl p-5 md:p-6 shadow-xl space-y-5"
      aria-label="Human in the loop action required"
    >
      <div class="flex items-start gap-3.5 border-b border-amber-900/50 pb-4">
        <span
          class="inline-flex items-center justify-center h-9 w-9 rounded-full bg-[var(--amber)] text-black font-extrabold text-base shrink-0 mt-0.5"
        >
          !
        </span>
        <div class="space-y-1">
          <h2 class="text-base sm:text-lg font-bold text-[var(--amber)]">
            {wantsInput ? 'Input Required to Continue' : 'Review & Approve Application Submission'}
          </h2>
          <p class="text-xs text-[var(--chalk)]">
            {wantsInput
              ? 'The application form encountered a question that requires your personal input.'
              : 'Vanguard completed filling the form and paused safely. No application is sent without your approval.'}
          </p>
        </div>
      </div>

      <!-- Question / Reason Box -->
      <div class="p-4 rounded-xl bg-[var(--charcoal)] border border-[var(--hairline)] space-y-1.5">
        <span class="text-[11px] font-semibold uppercase tracking-wider text-[var(--amber)]">
          {wantsInput ? 'Question / Prompt from Site' : 'Submission Summary'}
        </span>
        <p class="text-sm font-medium text-[var(--snow)] leading-relaxed">
          {approval.reason}
        </p>
      </div>

      <!-- HITL Interactive Forms -->
      {#if wantsInput}
        <form
          method="POST"
          action="?/answer"
          use:enhance={() => {
            isSubmitting = true;
            return async ({ update }) => {
              isSubmitting = false;
              await update();
            };
          }}
          class="space-y-4"
        >
          <div class="form-control w-full">
            <label for="answer" class="label pb-1.5">
              <span class="label-text text-xs font-semibold text-[var(--chalk)]">Your Answer</span>
            </label>
            <textarea
              id="answer"
              name="answer"
              rows="3"
              maxlength="2000"
              required
              disabled={isSubmitting}
              placeholder="Type your response to the question above..."
              class="textarea textarea-bordered w-full bg-[var(--charcoal)] border-[var(--hairline)] text-[var(--snow)] text-sm rounded-xl focus:border-[var(--blue)] focus:outline-none"
            ></textarea>
          </div>

          <div class="flex items-center justify-end gap-3 pt-1">
            <button
              type="submit"
              disabled={isSubmitting}
              class="btn btn-primary bg-[var(--blue)] hover:bg-blue-600 border-none text-white text-sm font-medium px-6 rounded-xl shadow-sm transition-all flex items-center gap-2"
            >
              {#if isSubmitting}
                <span class="loading loading-spinner loading-xs"></span>
                Submitting answer...
              {:else}
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M14 5l7 7m0 0l-7 7m7-7H3"
                  />
                </svg>
                Submit Answer & Resume
              {/if}
            </button>
          </div>
        </form>
      {:else}
        <!-- Approval Form -->
        <form
          method="POST"
          action="?/approve"
          use:enhance={() => {
            isSubmitting = true;
            return async ({ update }) => {
              isSubmitting = false;
              await update();
            };
          }}
          class="space-y-4"
        >
          <div class="form-control w-full">
            <label for="note" class="label pb-1.5">
              <span class="label-text text-xs font-medium text-[var(--chalk)]"
                >Approval Note (Optional)</span
              >
            </label>
            <input
              id="note"
              name="note"
              maxlength="500"
              disabled={isSubmitting}
              placeholder="e.g. Reviewed details, ready to submit"
              class="input input-bordered w-full bg-[var(--charcoal)] border-[var(--hairline)] text-[var(--snow)] text-sm rounded-xl focus:border-[var(--amber)] focus:outline-none"
            />
          </div>

          <div class="flex items-center justify-end gap-3 pt-1">
            <button
              type="submit"
              disabled={isSubmitting}
              class="btn bg-[var(--amber)] text-black hover:bg-amber-400 border-none text-sm font-semibold px-6 rounded-xl shadow-sm transition-all flex items-center gap-2"
            >
              {#if isSubmitting}
                <span class="loading loading-spinner loading-xs"></span>
                Authorizing submission...
              {:else}
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                Approve & Submit Application
              {/if}
            </button>
          </div>
        </form>
      {/if}

      <!-- Detailed Submission Payload Details -->
      {#if approval.details && !wantsInput}
        <details
          class="p-3.5 rounded-xl bg-[var(--charcoal)] border border-[var(--hairline)] text-xs group"
        >
          <summary
            class="font-medium text-[var(--chalk)] cursor-pointer hover:text-[var(--snow)] flex items-center justify-between"
          >
            <span>Inspect Prepared Submission Details</span>
            <span class="text-[11px] text-[var(--steel)] group-open:rotate-180 transition-transform"
              >▼</span
            >
          </summary>
          <div class="mt-3 pt-3 border-t border-[var(--hairline)]">
            <pre
              class="overflow-x-auto p-3 rounded-lg bg-[var(--void)] text-[var(--snow)] font-mono text-[11px] leading-relaxed">{JSON.stringify(
                approval.details,
                null,
                2,
              )}</pre>
          </div>
        </details>
      {/if}
    </section>
  {/if}

  <!-- Job Discovery Results (if any) -->
  {#if data.jobs.length > 0}
    <section
      class="bg-[var(--graphite)] border border-[var(--hairline)] rounded-2xl p-5 md:p-6 shadow-sm space-y-4"
    >
      <div class="flex items-center justify-between border-b border-[var(--hairline)] pb-4">
        <div>
          <h2 class="text-base font-semibold text-[var(--snow)]">Discovered Job Listings</h2>
          <p class="text-xs text-[var(--fog)] mt-0.5">
            Found {data.jobs.length} verified listings on the web.
          </p>
        </div>
        <span class="badge badge-sm badge-info font-mono">{data.jobs.length}</span>
      </div>

      <ul class="divide-y divide-[var(--hairline)]">
        {#each data.jobs as job (job.id)}
          <li class="py-3.5 first:pt-0 last:pb-0 space-y-1">
            <div class="flex items-start justify-between gap-3">
              <a
                href={job.source_url}
                target="_blank"
                rel="noreferrer noopener"
                class="font-medium text-sm text-[var(--snow)] hover:text-[var(--arc-blue)] transition-colors inline-flex items-center gap-1.5"
              >
                {job.title}
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-3 w-3 shrink-0 opacity-70"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                  />
                </svg>
              </a>
              {#if job.location}
                <span
                  class="badge badge-sm bg-[var(--charcoal)] border-[var(--hairline)] text-[var(--chalk)] text-[11px] shrink-0"
                >
                  {job.location}
                </span>
              {/if}
            </div>
            <div class="text-xs text-[var(--steel)] flex items-center gap-2">
              <span class="text-[var(--fog)]">{job.company ?? 'Unknown Company'}</span>
            </div>
            {#if job.description}
              <p class="text-xs text-[var(--fog)] line-clamp-2 pt-0.5">
                {job.description}
              </p>
            {/if}
          </li>
        {/each}
      </ul>
    </section>
  {/if}

  <!-- Task Payload & Execution Telemetry Details -->
  <details
    class="bg-[var(--graphite)] border border-[var(--hairline)] rounded-2xl p-4 text-xs shadow-sm group"
  >
    <summary
      class="font-medium text-[var(--chalk)] cursor-pointer hover:text-[var(--snow)] flex items-center justify-between"
    >
      <span>Raw Task Payload & Execution Result (JSON)</span>
      <span class="text-[11px] text-[var(--steel)] group-open:rotate-180 transition-transform"
        >▼</span
      >
    </summary>
    <div class="mt-3 pt-3 border-t border-[var(--hairline)]">
      <pre
        class="overflow-x-auto p-3 rounded-lg bg-[var(--void)] text-[var(--snow)] font-mono text-[11px] leading-relaxed">{JSON.stringify(
          { payload: task.payload, result: task.result },
          null,
          2,
        )}</pre>
    </div>
  </details>
</div>
