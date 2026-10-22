<script lang="ts">
  import { invalidateAll } from '$app/navigation';
  import { page } from '$app/state';

  let { data, form } = $props();

  const tasks = $derived(data.tasks);
  const running = $derived(tasks.some((t) => t.status === 'running' || t.status === 'queued'));
</script>

{#if form?.error}
  <p class="error" role="alert">{form.error}</p>
{/if}

<div class="grid">
  <section class="card">
    <h2>Tasks</h2>
    {#if tasks.length === 0}
      <p class="empty">No tasks yet. Start a discovery run to find real job postings.</p>
    {:else}
      <table>
        <thead>
          <tr>
            <th>Type</th>
            <th>Status</th>
            <th>Created</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {#each tasks as task (task.id)}
            <tr>
              <td>{task.type}</td>
              <td><span class="badge {task.status}">{task.status.replaceAll('_', ' ')}</span></td>
              <td class="muted">{new Date(task.created_at).toLocaleString()}</td>
              <td><a href="/tasks/{task.id}">Open</a></td>
            </tr>
          {/each}
        </tbody>
      </table>
    {/if}
    <div class="actions">
      <button class="secondary" onclick={() => invalidateAll()}>Refresh</button>
      {#if running}
        <span class="muted">Work in progress — open a task to follow it.</span>
      {/if}
    </div>
  </section>

  <div>
    <section class="card">
      <h2>Find jobs</h2>
      <p class="muted">Searches the live web and stores only listings it actually saw.</p>
      <form method="POST" action="?/discover">
        <div class="field">
          <label for="query">Search query</label>
          <input id="query" name="query" required minlength="2" maxlength="200" placeholder="backend engineer remote" />
        </div>
        <div class="field">
          <label for="limit">Max results</label>
          <input id="limit" name="limit" type="number" min="1" max="50" value="20" />
        </div>
        <div class="actions">
          <button type="submit">Start discovery</button>
        </div>
      </form>
    </section>

    <section class="card">
      <h2>Apply to a job URL</h2>
      <p class="muted">
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
        <div class="actions">
          <button type="submit">Prepare application</button>
        </div>
      </form>
    </section>
  </div>
</div>
