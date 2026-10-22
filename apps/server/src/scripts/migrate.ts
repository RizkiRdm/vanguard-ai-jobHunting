import { readdir, readFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { getDb, closeDb } from '../lib/db.ts';
import { logger } from '../lib/logger.ts';

const migrationsDir = resolve(
  dirname(fileURLToPath(import.meta.url)),
  '../../../../supabase/migrations',
);

/**
 * Applies every unapplied SQL file in supabase/migrations, in filename order.
 * Each file runs inside its own transaction so a failure leaves the schema clean.
 */
export async function runMigrations(): Promise<string[]> {
  const sql = getDb();
  await sql`
    create table if not exists public.schema_migrations (
      name text primary key,
      applied_at timestamptz not null default now()
    )
  `;

  const applied = new Set(
    (await sql<{ name: string }[]>`select name from public.schema_migrations`).map((r) => r.name),
  );

  const files = (await readdir(migrationsDir)).filter((f) => f.endsWith('.sql')).sort();
  const executed: string[] = [];

  for (const file of files) {
    if (applied.has(file)) continue;
    const statements = await readFile(join(migrationsDir, file), 'utf8');
    await sql.begin(async (tx) => {
      await tx.unsafe(statements);
      await tx`insert into public.schema_migrations (name) values (${file})`;
    });
    executed.push(file);
    logger.info('migration_applied', { file });
  }

  return executed;
}

const isDirectRun =
  process.argv[1] && import.meta.url.endsWith(process.argv[1].split('/').pop() ?? '');
if (isDirectRun) {
  runMigrations()
    .then((files) => {
      logger.info('migrations_complete', { applied: files.length });
      return closeDb();
    })
    .then(() => process.exit(0))
    .catch((err: unknown) => {
      logger.error('migration_failed', { error: err instanceof Error ? err.message : String(err) });
      process.exit(1);
    });
}
