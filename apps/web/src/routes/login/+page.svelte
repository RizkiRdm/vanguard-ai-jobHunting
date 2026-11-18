<script lang="ts">
  import { createBrowserClient } from '@supabase/ssr';
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import { authErrorMessage, CONFIRM_EMAIL_INFO, signupOutcome } from '../../lib/auth';
  import PasswordInput from '../../lib/components/PasswordInput.svelte';

  let { data } = $props();

  const urlMode = page.url.searchParams.get('mode');
  let mode = $state<'signin' | 'signup'>(urlMode === 'signup' ? 'signup' : 'signin');
  let email = $state('');
  let password = $state('');
  let pending = $state(false);
  let googlePending = $state(false);

  const initialError = page.url.searchParams.get('error');
  let errorMessage = $state(
    initialError === 'oauth_failed'
      ? 'Google sign-in was cancelled or failed. Please try again.'
      : initialError
        ? authErrorMessage(initialError)
        : '',
  );
  let infoMessage = $state('');

  const targetPath = $derived(page.url.searchParams.get('redirectTo') || '/dashboard');

  let client: ReturnType<typeof createBrowserClient> | null = null;
  function getClient() {
    client ??= createBrowserClient(data.supabaseUrl, data.supabaseKey);
    return client;
  }

  async function submit(event: SubmitEvent) {
    event.preventDefault();
    errorMessage = '';
    infoMessage = '';
    pending = true;
    try {
      if (mode === 'signin') {
        const { error } = await getClient().auth.signInWithPassword({ email, password });
        if (error) {
          errorMessage = authErrorMessage(error.message);
          return;
        }
        await goto(targetPath, { invalidateAll: true });
      } else {
        const { data: signUpData, error } = await getClient().auth.signUp({ email, password });
        if (error) {
          errorMessage = authErrorMessage(error.message);
          return;
        }
        if (signupOutcome(Boolean(signUpData.session)).kind === 'session') {
          await goto(targetPath, { invalidateAll: true });
        } else {
          infoMessage = CONFIRM_EMAIL_INFO;
          mode = 'signin';
        }
      }
    } finally {
      pending = false;
    }
  }

  async function signInWithGoogle() {
    errorMessage = '';
    infoMessage = '';
    googlePending = true;
    try {
      const callbackUrl = new URL('/auth/callback', window.location.origin);
      if (targetPath && targetPath !== '/dashboard') {
        callbackUrl.searchParams.set('next', targetPath);
      }
      const { error } = await getClient().auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: callbackUrl.toString(),
        },
      });
      if (error) {
        errorMessage = authErrorMessage(error.message);
      }
    } catch {
      errorMessage = 'Failed to initialize Google authentication.';
    } finally {
      googlePending = false;
    }
  }
</script>

<div class="auth-wrap flex min-h-[calc(100vh-80px)] items-center justify-center p-4">
  <div
    class="auth-card card w-full max-w-md bg-[var(--graphite)] shadow-xl border border-[var(--hairline)] rounded-2xl p-6 sm:p-8"
  >
    <h1 class="text-2xl sm:text-3xl font-normal text-[var(--snow)] mb-2">
      {mode === 'signin' ? 'Sign in' : 'Create account'}
    </h1>
    <p class="lead text-sm text-[var(--fog)] mb-6">
      Vanguard uses Supabase Auth. Credentials are never stored by this app.
    </p>

    <!-- Social Auth -->
    <button
      type="button"
      class="btn w-full bg-[var(--charcoal)] hover:bg-[var(--smoke)] text-[var(--snow)] border-[var(--hairline)] flex items-center justify-center gap-3 h-11"
      onclick={signInWithGoogle}
      disabled={googlePending || pending}
    >
      <svg class="h-5 w-5" viewBox="0 0 24 24" aria-hidden="true">
        <path
          fill="#4285F4"
          d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17z"
        />
        <path
          fill="#34A853"
          d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.33 24 12 24z"
        />
        <path
          fill="#FBBC05"
          d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.99 0 12s.45 3.82 1.25 5.42l4.03-3.15z"
        />
        <path
          fill="#EA4335"
          d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"
        />
      </svg>
      <span>{googlePending ? 'Connecting…' : 'Continue with Google'}</span>
    </button>

    <div class="divider text-xs text-[var(--steel)] my-6">OR</div>

    <!-- Mode Switcher -->
    <div
      class="auth-switch grid grid-cols-2 p-1 bg-[var(--charcoal)] rounded-xl border border-[var(--hairline)] mb-6"
      role="tablist"
    >
      <button
        type="button"
        class="py-2 text-sm font-medium rounded-lg transition-colors {mode === 'signin'
          ? 'bg-[var(--graphite)] text-[var(--snow)] shadow-sm'
          : 'text-[var(--fog)] hover:text-[var(--snow)]'}"
        aria-pressed={mode === 'signin'}
        onclick={() => {
          mode = 'signin';
          errorMessage = '';
          infoMessage = '';
        }}
      >
        Sign in
      </button>
      <button
        type="button"
        class="py-2 text-sm font-medium rounded-lg transition-colors {mode === 'signup'
          ? 'bg-[var(--graphite)] text-[var(--snow)] shadow-sm'
          : 'text-[var(--fog)] hover:text-[var(--snow)]'}"
        aria-pressed={mode === 'signup'}
        onclick={() => {
          mode = 'signup';
          errorMessage = '';
          infoMessage = '';
        }}
      >
        Create account
      </button>
    </div>

    <!-- Email & Password Form -->
    <form onsubmit={submit} class="space-y-4">
      <div class="form-control w-full">
        <label class="label py-1" for="email">
          <span class="label-text text-sm font-medium text-[var(--snow)]">Email</span>
        </label>
        <input
          id="email"
          type="email"
          required
          autocomplete="email"
          bind:value={email}
          placeholder="name@example.com"
          class="input input-bordered w-full bg-[var(--charcoal)] text-[var(--snow)] border-[var(--hairline)] focus:border-[var(--arc-blue)] focus:outline-none focus:ring-2 focus:ring-[var(--ring-blue)]"
        />
      </div>

      <PasswordInput
        id="password"
        label="Password"
        required={true}
        minlength={8}
        autocomplete={mode === 'signin' ? 'current-password' : 'new-password'}
        bind:value={password}
      />

      {#if errorMessage}
        <div class="alert alert-error text-sm py-2 px-3 rounded-lg border border-[var(--coral)] bg-red-950/40 text-red-200" role="alert">
          <span>{errorMessage}</span>
        </div>
      {/if}
      {#if infoMessage}
        <div class="alert alert-info text-sm py-2 px-3 rounded-lg border border-[var(--arc-blue)] bg-blue-950/40 text-blue-200" role="status">
          <span>{infoMessage}</span>
        </div>
      {/if}

      <div class="pt-2">
        <button
          class="btn btn-primary w-full bg-[var(--bone)] text-[var(--ink)] hover:bg-white border-none font-medium h-11"
          type="submit"
          disabled={pending || googlePending}
        >
          {pending ? 'Working…' : mode === 'signin' ? 'Sign in' : 'Create account'}
        </button>
      </div>
    </form>

    <p class="auth-footnote text-xs text-[var(--steel)] mt-6 text-center leading-relaxed">
      By signing in you agree to use Vanguard only on sites you are authorized to access.
    </p>
  </div>
</div>
