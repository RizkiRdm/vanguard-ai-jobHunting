import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import { getEnv } from '../config/env.ts';
import * as schema from '../db/schema.ts';

export type Sql = ReturnType<typeof postgres>;
export type Db = ReturnType<typeof drizzle<typeof schema>>;

let client: Sql | undefined;
let database: Db | undefined;

/**
 * Shared Postgres pool. `prepare: false` because the app connects through the
 * transaction-mode pooler, which does not support prepared statements.
 * `onnotice` is muted so Postgres notices never reach logs; SQL text is never logged.
 */
export function getDb(): Sql {
  if (!client) {
    client = postgres(getEnv().DATABASE_URL, {
      max: 10,
      idle_timeout: 30,
      connect_timeout: 10,
      prepare: false,
      onnotice: () => {},
    });
  }
  return client;
}

export function getDrizzle(): Db {
  if (!database) {
    database = drizzle(getDb(), { schema });
  }
  return database;
}

export async function closeDb(): Promise<void> {
  if (client) {
    await client.end({ timeout: 5 });
    client = undefined;
    database = undefined;
  }
}
