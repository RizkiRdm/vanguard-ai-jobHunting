<script lang="ts">
  import type { HTMLInputAttributes } from 'svelte/elements';

  interface Props {
    id: string;
    name?: string;
    label?: string;
    value: string;
    required?: boolean;
    minlength?: number;
    autocomplete?: HTMLInputAttributes['autocomplete'];
    placeholder?: string;
    errorMessage?: string;
    oninput?: (val: string) => void;
  }

  let {
    id,
    name = id,
    label = 'Password',
    value = $bindable(),
    required = false,
    minlength = 8,
    autocomplete = 'current-password',
    placeholder = '',
    errorMessage = '',
  }: Props = $props();

  let showPassword = $state(false);

  function toggleVisibility() {
    showPassword = !showPassword;
  }
</script>

<div class="form-control w-full">
  {#if label}
    <label class="label py-1" for={id}>
      <span class="label-text text-sm font-medium text-[var(--snow)]">{label}</span>
    </label>
  {/if}
  <div class="relative w-full">
    <input
      {id}
      {name}
      type={showPassword ? 'text' : 'password'}
      {required}
      {minlength}
      {autocomplete}
      {placeholder}
      bind:value
      class="input input-bordered w-full pr-11 bg-[var(--charcoal)] text-[var(--snow)] border-[var(--hairline)] focus:border-[var(--arc-blue)] focus:outline-none focus:ring-2 focus:ring-[var(--ring-blue)]"
      aria-invalid={errorMessage ? 'true' : undefined}
      aria-describedby={errorMessage ? `${id}-error` : undefined}
    />
    <button
      type="button"
      class="absolute right-2 top-1/2 -translate-y-1/2 btn btn-ghost btn-circle btn-sm text-[var(--fog)] hover:text-[var(--snow)] focus:outline-none focus:ring-2 focus:ring-[var(--ring-blue)]"
      onclick={toggleVisibility}
      aria-label={showPassword ? 'Hide password' : 'Show password'}
      aria-pressed={showPassword}
    >
      {#if showPassword}
        <!-- Eye off icon -->
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-4 w-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2"
          aria-hidden="true"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18"
          />
        </svg>
      {:else}
        <!-- Eye icon -->
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-4 w-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2"
          aria-hidden="true"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
          />
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
          />
        </svg>
      {/if}
    </button>
  </div>
  {#if errorMessage}
    <p id="{id}-error" class="text-xs text-[var(--coral)] mt-1" role="alert">
      {errorMessage}
    </p>
  {/if}
</div>
