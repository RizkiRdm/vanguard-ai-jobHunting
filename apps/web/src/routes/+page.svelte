<script lang="ts">
  import { invalidateAll } from '$app/navigation';
  import StatusBadge from '../lib/components/StatusBadge.svelte';

  let { data, form } = $props();

  const tasks = $derived(data.tasks);
  const jobs = $derived(data.jobs ?? []);
  const jobsError = $derived(data.jobsError);
  const running = $derived(tasks.some((t) => t.status === 'running' || t.status === 'queued'));
</script>

{#if form?.error}
  <p class="form-status error" role="alert">{form.error}</p>
{/if}
{#if form?.created}
  <p class="form-status success" role="status">
    Task created. <a href="/tasks/{form.created}">Open task {form.created}</a>.
  </p>
{/if}

<div class="dashboard-layout">
  <section class="panel">
    <div class="panel-header">
      <h2 class="panel-title">Tasks</h2>
      <div class="btn-row">
        <button class="btn btn-secondary btn-small" onclick={() => invalidateAll()}>Refresh</button>
        {#if running}
          <span class="muted micro">Work in progress — open a task to follow it.</span>
        {/if}
      </div>
    </div>

    {#if tasks.length === 0}
      <p class="empty-state">No tasks yet. Start a discovery run to find real job postings.</p>
    {:else}
      <ul class="task-list">
        {#each tasks as task (task.id)}
          <li class="task-card">
            <div class="task-card-main">
              <div class="task-summary">
                <div class="task-summary-top">
                  <span class="task-title">{task.type}</span>
                  <StatusBadge status={task.status} />
                </div>
                <div class="task-meta">
                  <span class="task-id">{task.id}</span>
                  <span class="muted micro">{new Date(task.created_at).toLocaleString()}</span>
                </div>
              </div>
              <a class="btn btn-quiet btn-small" href="/tasks/{task.id}">Open</a>
            </div>
          </li>
        {/each}
      </ul>
    {/if}
  </section>

  <div class="dashboard-side">
    <section class="panel">
      <h2 class="panel-title">Find jobs</h2>
      <p class="panel-description">
        Searches the live web and stores only listings it actually saw.
      </p>
      <form method="POST" action="?/discover">
        <div class="field">
          <label for="query">Search query</label>
          <input
            id="query"
            name="query"
            required
            minlength="2"
            maxlength="200"
            placeholder="backend engineer remote"
          />
        </div>
        <div class="field">
          <label for="limit">Max results</label>
          <input id="limit" name="limit" type="number" min="1" max="50" value="20" />
        </div>
        <div class="btn-row">
          <button class="btn btn-primary" type="submit">Start discovery</button>
        </div>
      </form>
    </section>

    <section class="panel">
      <h2 class="panel-title">Apply to a job URL</h2>
      <p class="panel-description">
        Vanguard fills the form and stops before submitting. You approve every submission.
      </p>
      <form method="POST" action="?/apply">
        <div class="field">
          <label for="source_url">Job posting URL</label>
          <input id="source_url" name="source_url" type="url" required placeholder="https://…" />
        </div>
        <div class="field">
          <label for="title">Job title (optional)</label>
          <input id="title" name="title" maxlength="200" />
        </div>
        <div class="field">
          <label for="company">Company (optional)</label>
          <input id="company" name="company" maxlength="200" />
        </div>
        <div class="btn-row">
          <button class="btn btn-primary" type="submit">Prepare application</button>
        </div>
      </form>
    </section>

    <section class="panel">
      <h2 class="panel-title">Recent listings</h2>
      {#if jobsError}
        <p class="form-status error" role="alert">{jobsError}</p>
      {:else if jobs.length === 0}
        <p class="empty-state">No listings yet. Run a discovery task to populate this list.</p>
      {:else}
        <ul class="listing-list">
          {#each jobs as job (job.id)}
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
      {/if}
    </section>
  </div>
</div>
