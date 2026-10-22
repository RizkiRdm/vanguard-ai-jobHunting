<script lang="ts">
  let { data, form } = $props();

  const profile = $derived(data.profile);
  let uploading = $state(false);
</script>

<div class="grid">
  <section class="card">
    <h2>Profile</h2>
    <p class="muted">Used to fill application forms. Stored in your own Supabase rows only.</p>

    {#if form?.error}
      <p class="error" role="alert">{form.error}</p>
    {:else if form?.saved}
      <p class="notice">Profile saved.</p>
    {:else if form?.uploaded}
      <p class="notice">Resume uploaded.</p>
    {:else if form?.deleted}
      <p class="notice">Resume removed.</p>
    {/if}

    <form method="POST" action="?/save">
      <div class="field">
        <label for="full_name">Full name</label>
        <input id="full_name" name="full_name" maxlength="255" value={profile?.full_name ?? ''} />
      </div>
      <div class="field">
        <label for="email">Email</label>
        <input id="email" name="email" type="email" maxlength="255" value={profile?.email ?? ''} />
      </div>
      <div class="field">
        <label for="phone">Phone</label>
        <input id="phone" name="phone" maxlength="50" value={profile?.phone ?? ''} />
      </div>
      <div class="field">
        <label for="target_role">Target role</label>
        <input id="target_role" name="target_role" maxlength="255" value={profile?.target_role ?? ''} />
      </div>
      <div class="field">
        <label for="location">Location</label>
        <input id="location" name="location" maxlength="255" value={profile?.location ?? ''} />
      </div>
      <div class="field">
        <label for="expected_salary">Expected salary</label>
        <input id="expected_salary" name="expected_salary" maxlength="100" value={profile?.expected_salary ?? ''} />
      </div>
      <div class="field">
        <label for="experience_years">Years of experience</label>
        <input
          id="experience_years"
          name="experience_years"
          type="number"
          min="0"
          max="80"
          value={profile?.experience_years ?? ''}
        />
      </div>
      <div class="field">
        <label for="skills">Skills (comma separated)</label>
        <input id="skills" name="skills" value={profile?.skills?.join(', ') ?? ''} />
      </div>
      <div class="field">
        <label for="summary">Summary</label>
        <textarea id="summary" name="summary" maxlength="4000">{profile?.summary ?? ''}</textarea>
      </div>
      <div class="actions">
        <button type="submit">Save profile</button>
      </div>
    </form>
  </section>

  <section class="card">
    <h2>Resume</h2>
    <p class="muted">PDF only, up to 10 MB. Stored in a private bucket with a random object name.</p>

    {#if profile?.resume_filename}
      <p>
        <a href="/profile/resume">{profile.resume_filename}</a>
        <span class="muted">(link expires in 60 seconds)</span>
      </p>
      <form method="POST" action="?/deleteResume">
        <button class="danger" type="submit">Remove resume</button>
      </form>
    {:else}
      <p class="empty">No resume uploaded yet.</p>
    {/if}

    <form
      method="POST"
      action="?/uploadResume"
      enctype="multipart/form-data"
      onsubmit={() => (uploading = true)}
    >
      <div class="field" style="margin-top:12px">
        <label for="file">{profile?.resume_filename ? 'Replace resume' : 'Upload resume'}</label>
        <input id="file" name="file" type="file" accept="application/pdf" required />
      </div>
      <div class="actions">
        <button type="submit" disabled={uploading}>{uploading ? 'Uploading…' : 'Upload PDF'}</button>
      </div>
    </form>
  </section>
</div>
