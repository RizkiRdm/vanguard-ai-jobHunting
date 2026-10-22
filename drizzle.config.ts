import { defineConfig } from 'drizzle-kit';

// Introspection only. Schema changes go through supabase/migrations.
try {
  process.loadEnvFile();
} catch {
  // CI passes DATABASE_URL directly.
}

export default defineConfig({
  schema: './apps/server/src/db/schema.ts',
  out: './apps/server/drizzle',
  dialect: 'postgresql',
  dbCredentials: { url: process.env.DATABASE_URL ?? '' },
});
