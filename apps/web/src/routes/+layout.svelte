<script lang="ts">
  import '../app.css';
  import { page } from '$app/state';

  let { data, children } = $props();
</script>

<header class="app-header border-b border-[var(--hairline)] bg-[var(--void)]/90 backdrop-blur sticky top-0 z-50">
  <div class="header-inner max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
    <div class="flex items-center gap-3">
      <a class="brand flex items-center gap-2 text-[var(--snow)] font-semibold" href={data.user ? '/dashboard' : '/'}>
        <span class="brand-mark h-7 w-7 rounded-lg bg-[var(--bone)] text-[var(--ink)] flex items-center justify-center font-bold text-sm">V</span>
        <span class="brand-name text-base tracking-tight">Vanguard</span>
      </a>
      <span class="brand-note hidden md:inline text-xs text-[var(--steel)] border-l border-[var(--hairline)] pl-3">
        Autonomous job discovery & application drafting
      </span>
    </div>
    <nav class="app-nav flex items-center gap-4">
      {#if data.user}
        <a class="nav-link text-sm text-[var(--chalk)] hover:text-white transition-colors" href="/dashboard">Dashboard</a>
        <a class="nav-link text-sm text-[var(--chalk)] hover:text-white transition-colors" href="/profile">Profile</a>
        <form method="POST" action="/logout">
          <button class="btn btn-secondary btn-small text-xs py-1 px-3 rounded-lg border border-[var(--hairline)] text-[var(--snow)] hover:bg-[var(--charcoal)]" type="submit">
            Sign out
          </button>
        </form>
      {:else}
        <a class="nav-link text-sm text-[var(--chalk)] hover:text-white transition-colors" href="/login">Sign in</a>
        <a class="btn btn-primary btn-small text-xs py-1.5 px-3 rounded-lg bg-[var(--bone)] text-[var(--ink)] hover:bg-white font-medium transition-colors" href="/login?mode=signup">
          Get started
        </a>
      {/if}
    </nav>
  </div>
</header>

<main class="max-w-6xl mx-auto px-4 sm:px-6 py-6 min-h-[calc(100vh-120px)]">
  {@render children()}
</main>

{#if page.error}
  <div class="max-w-6xl mx-auto px-4 mb-4">
    <div class="alert alert-error text-sm py-2 px-4 rounded-lg border border-[var(--coral)] bg-red-950/40 text-red-200" role="alert">
      <span>{page.error.message}</span>
    </div>
  </div>
{/if}
