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

<div class="card" style="max-width:420px;margin:48px auto">
  <h2>{mode === 'signin' ? 'Sign in' : 'Create account'}</h2>
  <p class="muted">Vanguard uses Supabase Auth. Credentials are never stored by this app.</p>

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
      <p class="error" role="alert">{errorMessage}</p>
    {/if}
    {#if infoMessage}
      <p class="notice">{infoMessage}</p>
    {/if}

    <div class="actions">
      <button type="submit" disabled={pending}>
        {pending ? 'Working…' : mode === 'signin' ? 'Sign in' : 'Create account'}
      </button>
      <button
        type="button"
        class="secondary"
        onclick={() => {
          mode = mode === 'signin' ? 'signup' : 'signin';
          errorMessage = '';
          infoMessage = '';
        }}
      >
        {mode === 'signin' ? 'Create account' : 'Back to sign in'}
      </button>
    </div>
  </form>
</div>
