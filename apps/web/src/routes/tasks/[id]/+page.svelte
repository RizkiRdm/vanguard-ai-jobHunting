<script lang="ts">
  import { invalidateAll } from '$app/navigation';
  import StatusBadge from '../../../lib/components/StatusBadge.svelte';

  let { data, form } = $props();

  const task = $derived(data.task);
  const approval = $derived(task.approval);
  const wantsInput = $derived(approval?.details?.kind === 'input');
  const live = $derived(
    task.status === 'queued' || task.status === 'running' || task.status === 'waiting_for_user',
  );

  $effect(() => {
    if (!live) return;
    const id = setInterval(() => void invalidateAll(), 3000);
    return () => clearInterval(id);
  });

  function confirmCancel(event: SubmitEvent) {
    if (!confirm('Cancel this task?')) event.preventDefault();
  }
</script>

<p class="breadcrumb"><a href="/">← All tasks</a></p>

{#if form?.error}
  <p class="form-status error" role="alert">{form.error}</p>
{/if}
{#if form?.cancelled}
  <p class="form-status info" role="status">Task cancelled.</p>
{/if}

<section class="panel">
  <div class="task-summary-top">
    <h2 class="panel-title" style="margin:0">Task {task.type}</h2>
    <StatusBadge status={task.status} />
  </div>
  <p class="muted micro" style="margin-top:8px">
    Created {new Date(task.created_at).toLocaleString()} · Attempt {task.attempts}/{task.max_attempts}
    {#if live}· updating automatically{/if}
  </p>

  {#if task.status === 'failed' && task.error}
    <p class="form-status error">This task failed: {task.error}</p>
  {/if}

  {#if live}
    <form
      method="POST"
      action="?/cancel"
      onsubmit={confirmCancel}
      class="btn-row"
      style="margin-top:12px"
    >
      <button class="btn btn-secondary btn-small" type="submit">Cancel task</button>
    </form>
  {/if}
</section>

{#if task.status === 'waiting_for_user' && approval}
  <section class="panel approval-panel">
    <h2 class="panel-title">
      {wantsInput ? 'Your input is needed' : 'Approval required before submitting'}
    </h2>
    <p>{approval.reason}</p>

    {#if wantsInput}
      <form method="POST" action="?/answer">
        <div class="field">
          <label for="answer">Answer</label>
          <textarea id="answer" name="answer" maxlength="2000" required></textarea>
        </div>
        <div class="btn-row">
          <button class="btn btn-primary" type="submit">Submit answer</button>
        </div>
      </form>
    {:else}
      <p class="muted micro">
        Vanguard filled the form and stopped. Check the details, then approve the submission.
        Nothing is sent until you approve.
      </p>
      <form method="POST" action="?/approve">
        <div class="field">
          <label for="note">Note (optional)</label>
          <input id="note" name="note" maxlength="500" />
        </div>
        <div class="btn-row">
          <button class="btn btn-primary" type="submit">Approve and submit</button>
        </div>
      </form>
    {/if}

    {#if approval.details && !wantsInput}
      <details class="json-details">
        <summary>Submission details (JSON)</summary>
        <pre>{JSON.stringify(approval.details, null, 2)}</pre>
      </details>
    {/if}
  </section>
{/if}

<details class="json-details">
  <summary>Task payload and result (JSON)</summary>
  <pre>{JSON.stringify({ payload: task.payload, result: task.result }, null, 2)}</pre>
</details>

{#if data.jobs.length > 0}
  <section class="panel">
    <h2 class="panel-title">Found listings ({data.jobs.length})</h2>
    <ul class="listing-list">
      {#each data.jobs as job (job.id)}
        <li class="listing-card">
          <a href={job.source_url} rel="noreferrer noopener" target="_blank">{job.title}</a>
          <div class="muted micro">
            {job.company ?? 'Unknown company'}{job.location ? ` · ${job.location}` : ''}
          </div>
          {#if job.description}
            <p class="muted micro">{job.description}</p>
          {/if}
        </li>
      {/each}
    </ul>
  </section>
{/if}
