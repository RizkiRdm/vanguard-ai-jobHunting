<script lang="ts">
  import '../app.css';
  import { page } from '$app/state';

  let { data, children } = $props();
</script>

<header class="app-header">
  <div>
    <h1>Vanguard</h1>
    <p class="muted" style="margin:0">Autonomous job discovery and application drafting</p>
  </div>
  <nav>
    {#if data.user}
      <a href="/">Tasks</a>
      <a href="/profile">Profile</a>
      <form method="POST" action="/logout" style="margin:0">
        <button class="secondary" type="submit">Sign out</button>
      </form>
    {/if}
  </nav>
</header>

<main>
  {@render children()}
</main>

{#if page.error}
  <p class="error">{page.error.message}</p>
{/if}
