<script lang="ts">
  let { status }: { status: string } = $props();
</script>

<span class="status {status}">{status.replaceAll('_', ' ')}</span>
