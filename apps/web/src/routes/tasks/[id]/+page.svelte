<script lang="ts">
  import { invalidateAll } from '$app/navigation';

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
</script>

<p><a href="/">← All tasks</a></p>

{#if form?.error}
  <p class="error" role="alert">{form.error}</p>
{/if}

<section class="card">
  <div class="row" style="justify-content:space-between">
    <h2 style="margin:0">Task {task.type}</h2>
    <span class="badge {task.status}">{task.status.replaceAll('_', ' ')}</span>
  </div>

  <p class="muted" style="margin-top:8px">
    Created {new Date(task.created_at).toLocaleString()} · Attempt {task.attempts}/{task.max_attempts}
    {#if live}· updating automatically{/if}
  </p>

  {#if task.status === 'failed' && task.error}
    <p class="error">This task failed: {task.error}</p>
  {/if}

  {#if live}
    <div class="actions">
      <form method="POST" action="?/cancel">
        <button class="secondary" type="submit">Cancel task</button>
      </form>
    </div>
  {/if}
</section>

{#if task.status === 'waiting_for_user' && approval}
  <section class="card" style="border-color:#fde68a;background:#fffbeb">
    <h2>{wantsInput ? 'Your input is needed' : 'Approval required before submitting'}</h2>
    <p>{approval.reason}</p>

    {#if wantsInput}
      <form method="POST" action="?/answer">
        <div class="field">
          <label for="answer">Answer</label>
          <textarea id="answer" name="answer" maxlength="2000" required></textarea>
        </div>
        <div class="actions">
          <button type="submit">Submit answer</button>
        </div>
      </form>
    {:else}
      <p class="muted">
        Vanguard filled the form and stopped. Check the details, then approve the submission. Nothing
        is sent until you approve.
      </p>
      <form method="POST" action="?/approve">
        <div class="field">
          <label for="note">Note (optional)</label>
          <input id="note" name="note" maxlength="500" />
        </div>
        <div class="actions">
          <button type="submit">Approve and submit</button>
        </div>
      </form>
    {/if}

    {#if approval.details && !wantsInput}
      <pre class="details">{JSON.stringify(approval.details, null, 2)}</pre>
    {/if}
  </section>
{/if}

<section class="card">
  <h2>Details</h2>
  <pre class="details">{JSON.stringify({ payload: task.payload, result: task.result }, null, 2)}</pre>
</section>

{#if data.jobs.length > 0}
  <section class="card">
    <h2>Found listings ({data.jobs.length})</h2>
    <ul class="jobs">
      {#each data.jobs as job (job.id)}
        <li>
          <a href={job.source_url} rel="noreferrer noopener" target="_blank">{job.title}</a>
          <div class="muted">
            {job.company ?? 'Unknown company'}{job.location ? ` · ${job.location}` : ''}
          </div>
          {#if job.description}
            <p class="muted">{job.description}</p>
          {/if}
        </li>
      {/each}
    </ul>
  </section>
{/if}
