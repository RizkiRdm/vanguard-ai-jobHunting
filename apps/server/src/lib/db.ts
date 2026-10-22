import postgres, { type JSONValue } from 'postgres';
import { getEnv } from '../config/env.ts';

export type Sql = ReturnType<typeof postgres>;

/** Narrows an already-validated object for a JSONB parameter. */
export function toJson(value: unknown): JSONValue {
  return value as JSONValue;
}

let client: Sql | undefined;

/**
 * Shared Postgres pool. `onnotice` is muted so Postgres notices never reach logs.
 * SQL text itself is never logged (the Python app echoed every statement).
 */
export function getDb(): Sql {
  if (!client) {
    client = postgres(getEnv().DATABASE_URL, {
      max: 10,
      idle_timeout: 30,
      connect_timeout: 10,
      onnotice: () => {},
    });
  }
  return client;
}

export async function closeDb(): Promise<void> {
  if (client) {
    await client.end({ timeout: 5 });
    client = undefined;
  }
}
