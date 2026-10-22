import adapter from '@sveltejs/adapter-node';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  // Read the single .env at the repo root, shared with the API and worker.
  plugins: [sveltekit({ adapter: adapter(), env: { dir: '../../' } })],
});
