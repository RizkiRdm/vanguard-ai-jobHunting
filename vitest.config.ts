import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node',
    include: [
      'apps/server/src/**/*.test.ts',
      'apps/web/src/**/*.test.ts',
      'packages/*/src/**/*.test.ts',
      'scripts/**/*.test.mjs',
    ],
  },
});
