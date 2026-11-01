<script lang="ts">
  import '../app.css';
  import { page } from '$app/state';

  let { data, children } = $props();
</script>

<header class="app-header">
  <div class="header-inner">
    <a class="brand" href="/">
      <span class="brand-mark">V</span>
      <span class="brand-name">Vanguard</span>
    </a>
    <span class="brand-note">Autonomous job discovery and application drafting</span>
    <nav class="app-nav">
      {#if data.user}
        <a class="nav-link" href="/">Tasks</a>
        <a class="nav-link" href="/profile">Profile</a>
        <form method="POST" action="/logout">
          <button class="btn btn-secondary btn-small" type="submit">Sign out</button>
        </form>
      {/if}
    </nav>
  </div>
</header>

<main>
  {@render children()}
</main>

{#if page.error}
  <p class="error" role="alert">{page.error.message}</p>
{/if}
