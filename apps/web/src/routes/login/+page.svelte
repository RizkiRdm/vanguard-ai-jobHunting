<script lang="ts">
  import { createBrowserClient } from '@supabase/ssr';
  import { goto } from '$app/navigation';

  let { data } = $props();

  let mode = $state<'signin' | 'signup'>('signin');
  let email = $state('');
  let password = $state('');
  let pending = $state(false);
  let errorMessage = $state('');
  let infoMessage = $state('');

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
          errorMessage = error.message;
          return;
        }
        await goto('/', { invalidateAll: true });
      } else {
        const { data: signUpData, error } = await getClient().auth.signUp({ email, password });
        if (error) {
          errorMessage = error.message;
          return;
        }
        if (signUpData.session) {
          await goto('/', { invalidateAll: true });
        } else {
          infoMessage = 'Account created. Confirm your email, then sign in.';
          mode = 'signin';
        }
      }
    } finally {
      pending = false;
    }
  }
</script>

<div class="auth-wrap">
  <div class="auth-card">
    <h1>{mode === 'signin' ? 'Sign in' : 'Create account'}</h1>
    <p class="lead">Vanguard uses Supabase Auth. Credentials are never stored by this app.</p>

    <div class="auth-switch" role="tablist">
      <button
        type="button"
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

    <form onsubmit={submit}>
      <div class="field">
        <label for="email">Email</label>
        <input id="email" type="email" required autocomplete="email" bind:value={email} />
      </div>
      <div class="field">
        <label for="password">Password</label>
        <input
          id="password"
          type="password"
          required
          minlength="8"
          autocomplete={mode === 'signin' ? 'current-password' : 'new-password'}
          bind:value={password}
        />
      </div>

      {#if errorMessage}
        <p class="form-status error" role="alert">{errorMessage}</p>
      {/if}
      {#if infoMessage}
        <p class="form-status info">{infoMessage}</p>
      {/if}

      <div class="btn-row">
        <button class="btn btn-primary" type="submit" disabled={pending}>
          {pending ? 'Working…' : mode === 'signin' ? 'Sign in' : 'Create account'}
        </button>
      </div>
    </form>

    <p class="auth-footnote">
      By signing in you agree to use Vanguard only on sites you are authorized to access.
    </p>
  </div>
</div>
