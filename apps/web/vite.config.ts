import adapter from '@sveltejs/adapter-node';
import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  // Read the single .env at the repo root, shared with the API and worker.
  plugins: [tailwindcss(), sveltekit({ adapter: adapter(), env: { dir: '../../' } })],
});
