<script lang="ts">
  import { enhance } from '$app/forms';

  let { data, form } = $props();

  const profile = $derived(data.profile);

  type UploadPhase = 'idle' | 'uploading' | 'parsing' | 'success' | 'error';
  let uploadPhase = $state<UploadPhase>('idle');
  let selectedFileName = $state<string>('');

  $effect(() => {
    if (form?.uploaded) {
      uploadPhase = 'success';
    } else if (form?.error && uploadPhase !== 'idle') {
      uploadPhase = 'error';
    }
  });

  const extractedKeys = $derived(() => {
    if (!form?.extractedProfile) return [];
    return Object.entries(form.extractedProfile)
      .filter(([_, v]) => v !== undefined && v !== null && (Array.isArray(v) ? v.length > 0 : true))
      .map(([k]) => k.replace(/_/g, ' '));
  });
</script>

<div class="max-w-6xl mx-auto space-y-6">
  <!-- Page Header -->
  <header class="pb-2 border-b border-[var(--hairline)]">
    <h1 class="text-2xl font-bold tracking-tight text-[var(--snow)]">Candidate Profile</h1>
    <p class="text-sm text-[var(--fog)] mt-1">
      Manage your application credentials and resume. Stored securely in your private Supabase
      storage and rows.
    </p>
  </header>

  <!-- Status / Alert Banners -->
  {#if form?.error}
    <div
      class="alert alert-error text-sm py-3 px-4 rounded-xl border border-[var(--coral)] bg-red-950/40 text-red-200 shadow-sm"
      role="alert"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-5 w-5 shrink-0 stroke-current"
        fill="none"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <span>{form.error}</span>
    </div>
  {:else if form?.saved}
    <div
      class="alert alert-success text-sm py-3 px-4 rounded-xl border border-[var(--mint)] bg-emerald-950/40 text-emerald-200 shadow-sm"
      role="status"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-5 w-5 shrink-0 stroke-current"
        fill="none"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <span>Profile saved successfully.</span>
    </div>
  {:else if form?.uploaded}
    <div
      class="alert alert-success text-sm py-3 px-4 rounded-xl border border-[var(--mint)] bg-emerald-950/40 text-emerald-200 shadow-sm flex flex-col items-start gap-2"
      role="status"
    >
      <div class="flex items-center gap-2">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5 shrink-0 stroke-current"
          fill="none"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <span class="font-medium">Resume uploaded and analyzed!</span>
      </div>
      {#if extractedKeys().length > 0}
        <p class="text-xs text-emerald-300/90 pl-7">
          AI extracted and populated:
          <span class="capitalize font-semibold">{extractedKeys().join(', ')}</span>. Please review
          the details below.
        </p>
      {/if}
    </div>
  {:else if form?.deleted}
    <div
      class="alert text-sm py-3 px-4 rounded-xl border border-[var(--hairline)] bg-[var(--charcoal)] text-[var(--chalk)] shadow-sm"
      role="status"
    >
      <span>Resume removed.</span>
    </div>
  {/if}

  <!-- Main Grid: 2 cols for form, 1 col for resume upload -->
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <!-- Left: Profile Edit Form (lg:col-span-2) -->
    <section
      class="lg:col-span-2 bg-[var(--graphite)] border border-[var(--hairline)] rounded-2xl p-5 md:p-6 shadow-sm space-y-6"
    >
      <div class="border-b border-[var(--hairline)] pb-4">
        <h2 class="text-lg font-semibold text-[var(--snow)]">Application Details</h2>
        <p class="text-xs text-[var(--fog)] mt-0.5">
          These fields are used by the browser agent to auto-fill job application questions.
        </p>
      </div>

      <form method="POST" action="?/save" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Full Name -->
          <div class="form-control w-full">
            <label for="full_name" class="label pb-1.5">
              <span class="label-text text-xs font-medium text-[var(--chalk)]">Full Name</span>
            </label>
            <input
              id="full_name"
              name="full_name"
              maxlength="255"
              value={profile?.full_name ?? ''}
              placeholder="e.g. Jane Doe"
              class="input input-bordered w-full bg-[var(--charcoal)] border-[var(--hairline)] text-[var(--snow)] text-sm rounded-xl focus:border-[var(--blue)] focus:outline-none"
            />
          </div>

          <!-- Email -->
          <div class="form-control w-full">
            <label for="email" class="label pb-1.5">
              <span class="label-text text-xs font-medium text-[var(--chalk)]">Email Address</span>
            </label>
            <input
              id="email"
              name="email"
              type="email"
              maxlength="255"
              value={profile?.email ?? ''}
              placeholder="e.g. jane@example.com"
              class="input input-bordered w-full bg-[var(--charcoal)] border-[var(--hairline)] text-[var(--snow)] text-sm rounded-xl focus:border-[var(--blue)] focus:outline-none"
            />
          </div>

          <!-- Phone -->
          <div class="form-control w-full">
            <label for="phone" class="label pb-1.5">
              <span class="label-text text-xs font-medium text-[var(--chalk)]">Phone Number</span>
            </label>
            <input
              id="phone"
              name="phone"
              maxlength="50"
              value={profile?.phone ?? ''}
              placeholder="e.g. +1 (555) 012-3456"
              class="input input-bordered w-full bg-[var(--charcoal)] border-[var(--hairline)] text-[var(--snow)] text-sm rounded-xl focus:border-[var(--blue)] focus:outline-none"
            />
          </div>

          <!-- Target Role -->
          <div class="form-control w-full">
            <label for="target_role" class="label pb-1.5">
              <span class="label-text text-xs font-medium text-[var(--chalk)]">Target Role</span>
            </label>
            <input
              id="target_role"
              name="target_role"
              maxlength="255"
              value={profile?.target_role ?? ''}
              placeholder="e.g. Senior Frontend Engineer"
              class="input input-bordered w-full bg-[var(--charcoal)] border-[var(--hairline)] text-[var(--snow)] text-sm rounded-xl focus:border-[var(--blue)] focus:outline-none"
            />
          </div>

          <!-- Location -->
          <div class="form-control w-full">
            <label for="location" class="label pb-1.5">
              <span class="label-text text-xs font-medium text-[var(--chalk)]">Location</span>
            </label>
            <input
              id="location"
              name="location"
              maxlength="255"
              value={profile?.location ?? ''}
              placeholder="e.g. San Francisco, CA (or Remote)"
              class="input input-bordered w-full bg-[var(--charcoal)] border-[var(--hairline)] text-[var(--snow)] text-sm rounded-xl focus:border-[var(--blue)] focus:outline-none"
            />
          </div>

          <!-- Expected Salary -->
          <div class="form-control w-full">
            <label for="expected_salary" class="label pb-1.5">
              <span class="label-text text-xs font-medium text-[var(--chalk)]">Expected Salary</span
              >
            </label>
            <input
              id="expected_salary"
              name="expected_salary"
              maxlength="100"
              value={profile?.expected_salary ?? ''}
              placeholder="e.g. $160,000"
              class="input input-bordered w-full bg-[var(--charcoal)] border-[var(--hairline)] text-[var(--snow)] text-sm rounded-xl focus:border-[var(--blue)] focus:outline-none"
            />
          </div>

          <!-- Experience Years -->
          <div class="form-control w-full md:col-span-2">
            <label for="experience_years" class="label pb-1.5">
              <span class="label-text text-xs font-medium text-[var(--chalk)]"
                >Years of Experience</span
              >
            </label>
            <input
              id="experience_years"
              name="experience_years"
              type="number"
              min="0"
              max="80"
              value={profile?.experience_years ?? ''}
              placeholder="e.g. 5"
              class="input input-bordered w-full bg-[var(--charcoal)] border-[var(--hairline)] text-[var(--snow)] text-sm rounded-xl focus:border-[var(--blue)] focus:outline-none"
            />
          </div>

          <!-- Skills -->
          <div class="form-control w-full md:col-span-2">
            <label for="skills" class="label pb-1.5">
              <span class="label-text text-xs font-medium text-[var(--chalk)]"
                >Skills (comma separated)</span
              >
            </label>
            <input
              id="skills"
              name="skills"
              value={profile?.skills?.join(', ') ?? ''}
              placeholder="e.g. TypeScript, SvelteKit, Node.js, PostgreSQL, TailwindCSS"
              class="input input-bordered w-full bg-[var(--charcoal)] border-[var(--hairline)] text-[var(--snow)] text-sm rounded-xl focus:border-[var(--blue)] focus:outline-none"
            />
          </div>

          <!-- Summary -->
          <div class="form-control w-full md:col-span-2">
            <label for="summary" class="label pb-1.5">
              <span class="label-text text-xs font-medium text-[var(--chalk)]"
                >Professional Summary</span
              >
            </label>
            <textarea
              id="summary"
              name="summary"
              rows="4"
              maxlength="4000"
              placeholder="Brief professional background highlighting your key strengths and experience..."
              class="textarea textarea-bordered w-full bg-[var(--charcoal)] border-[var(--hairline)] text-[var(--snow)] text-sm rounded-xl focus:border-[var(--blue)] focus:outline-none"
              >{profile?.summary ?? ''}</textarea
            >
          </div>
        </div>

        <div class="flex items-center justify-end pt-3">
          <button
            type="submit"
            class="btn btn-primary bg-[var(--blue)] hover:bg-blue-600 border-none text-white text-sm font-medium px-6 rounded-xl shadow-sm transition-all"
          >
            Save Profile
          </button>
        </div>
      </form>
    </section>

    <!-- Right: Resume Upload & AI Analysis Panel (lg:col-span-1) -->
    <section
      class="bg-[var(--graphite)] border border-[var(--hairline)] rounded-2xl p-5 md:p-6 shadow-sm space-y-6"
    >
      <div class="border-b border-[var(--hairline)] pb-4">
        <h2 class="text-lg font-semibold text-[var(--snow)]">Resume & AI Autofill</h2>
        <p class="text-xs text-[var(--fog)] mt-0.5">
          PDF format only, up to 10 MB. Gemini AI will analyze your resume to prefill profile
          details.
        </p>
      </div>

      <!-- Current Resume Status Card -->
      {#if profile?.resume_filename}
        <div class="p-4 rounded-xl bg-[var(--charcoal)] border border-[var(--hairline)] space-y-3">
          <div class="flex items-start gap-3">
            <div class="p-2 rounded-lg bg-[var(--blue)]/10 text-[var(--arc-blue)] shrink-0">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <div class="min-w-0 flex-1">
              <p
                class="text-sm font-medium text-[var(--snow)] truncate"
                title={profile.resume_filename}
              >
                {profile.resume_filename}
              </p>
              <div class="flex items-center gap-2 mt-1">
                <a
                  href="/profile/resume"
                  class="text-xs text-[var(--arc-blue)] hover:underline inline-flex items-center gap-1"
                >
                  Download / View
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-3 w-3"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                    />
                  </svg>
                </a>
                <span class="text-[11px] text-[var(--steel)]">(expires in 60s)</span>
              </div>
            </div>
          </div>

          <form method="POST" action="?/deleteResume" class="pt-1">
            <button
              type="submit"
              class="btn btn-ghost btn-sm text-xs text-[var(--coral)] hover:bg-red-950/30 w-full rounded-lg"
            >
              Remove Resume
            </button>
          </form>
        </div>
      {:else}
        <div
          class="p-6 rounded-xl border border-dashed border-[var(--smoke)] text-center space-y-2 bg-[var(--charcoal)]/40"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-8 w-8 mx-auto text-[var(--steel)]"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
          <p class="text-xs text-[var(--chalk)]">No resume uploaded yet.</p>
          <p class="text-[11px] text-[var(--steel)]">
            Upload a PDF to parse contact info, skills, and experience.
          </p>
        </div>
      {/if}

      <!-- Dynamic Upload Form & Status Machine -->
      <form
        method="POST"
        action="?/uploadResume"
        enctype="multipart/form-data"
        use:enhance={() => {
          uploadPhase = 'uploading';
          // Switch to parsing indicator after brief upload delay
          const timer = setTimeout(() => {
            if (uploadPhase === 'uploading') {
              uploadPhase = 'parsing';
            }
          }, 1200);

          return async ({ update }) => {
            clearTimeout(timer);
            await update();
          };
        }}
        class="space-y-4"
      >
        <div class="form-control w-full">
          <label for="file" class="label pb-1.5">
            <span class="label-text text-xs font-medium text-[var(--chalk)]">
              {profile?.resume_filename ? 'Replace Resume (PDF)' : 'Choose Resume (PDF)'}
            </span>
          </label>
          <input
            id="file"
            name="file"
            type="file"
            accept="application/pdf"
            required
            disabled={uploadPhase === 'uploading' || uploadPhase === 'parsing'}
            onchange={(e) => {
              const files = (e.currentTarget as HTMLInputElement).files;
              selectedFileName = files && files[0] ? files[0].name : '';
            }}
            class="file-input file-input-bordered file-input-sm w-full bg-[var(--charcoal)] border-[var(--hairline)] text-[var(--snow)] rounded-xl text-xs"
          />
        </div>

        <!-- Dynamic Loading / Progress Indicators -->
        {#if uploadPhase === 'uploading'}
          <div
            class="p-3.5 rounded-xl bg-[var(--charcoal)] border border-[var(--hairline)] space-y-2"
            aria-live="polite"
          >
            <div class="flex items-center justify-between text-xs text-[var(--snow)]">
              <span class="inline-flex items-center gap-2">
                <span class="loading loading-spinner loading-xs text-[var(--blue)]"></span>
                Uploading document...
              </span>
              <span class="text-[var(--steel)]">Step 1 of 2</span>
            </div>
            <progress class="progress progress-primary w-full h-1.5 bg-[var(--smoke)]"></progress>
          </div>
        {:else if uploadPhase === 'parsing'}
          <div
            class="p-3.5 rounded-xl bg-[var(--charcoal)] border border-[var(--hairline)] space-y-2"
            aria-live="polite"
          >
            <div class="flex items-center justify-between text-xs text-[var(--snow)]">
              <span class="inline-flex items-center gap-2">
                <span class="loading loading-dots loading-xs text-[var(--amber)]"></span>
                Gemini AI extracting candidate data...
              </span>
              <span class="text-[var(--steel)]">Step 2 of 2</span>
            </div>
            <progress class="progress progress-warning w-full h-1.5 bg-[var(--smoke)]"></progress>
          </div>
        {/if}

        <button
          type="submit"
          disabled={uploadPhase === 'uploading' || uploadPhase === 'parsing'}
          class="btn btn-secondary w-full text-xs font-medium py-2 rounded-xl border border-[var(--hairline)] hover:bg-[var(--smoke)] text-[var(--snow)] transition-colors flex items-center justify-center gap-2"
        >
          {#if uploadPhase === 'uploading'}
            <span class="loading loading-spinner loading-xs"></span>
            Uploading...
          {:else if uploadPhase === 'parsing'}
            <span class="loading loading-spinner loading-xs"></span>
            Extracting profile...
          {:else}
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
              />
            </svg>
            Upload and Auto-fill Profile
          {/if}
        </button>
      </form>
    </section>
  </div>
</div>
