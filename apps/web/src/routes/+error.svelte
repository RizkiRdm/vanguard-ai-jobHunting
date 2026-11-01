<script lang="ts">
  import { page } from '$app/state';
</script>

<section class="panel">
  <h1>Something went wrong</h1>
  <p class="error" role="alert">{page.error?.message ?? 'Unexpected error.'}</p>
  <p><a href="/">Back to tasks</a></p>
</section>
