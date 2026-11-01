import { generateText, Output } from 'ai';
import { google } from '@ai-sdk/google';
import { sql } from 'drizzle-orm';
import type { z } from 'zod';
import { getEnv } from '../../config/env.ts';
import { llmUsageLog } from '../../db/schema.ts';
import { getDrizzle } from '../../lib/db.ts';
import { logger } from '../../lib/logger.ts';
import { AppError } from '../../lib/errors.ts';

/** Tokens reserved before a call so concurrent requests cannot overspend the cap. */
const RESERVATION_TOKENS = 4_000;

export interface GenerateOptions<T extends z.ZodTypeAny> {
  prompt: string;
  userId: string;
  schema: T;
  /** Base64 PNG screenshot, when the decision depends on the rendered page. */
  imageBase64?: string;
  /** Rules the page content cannot override. Sent as systemInstruction. */
  system?: string;
}

/**
 * Calls the model and returns schema-validated JSON.
 *
 * Budget is reserved atomically before the call (a single conditional UPDATE in
 * Postgres) and settled with the real usage afterwards, so parallel workers
 * cannot spend past the daily cap.
 */
export async function generateJson<T extends z.ZodTypeAny>(
  options: GenerateOptions<T>,
): Promise<z.infer<T>> {
  const env = getEnv();
  const db = getDrizzle();

  const reserved = (await db.execute(
    sql`select public.reserve_llm_tokens(${options.userId}, ${RESERVATION_TOKENS}, ${env.DAILY_TOKEN_BUDGET}) as reserved`,
  )) as unknown as Array<{ reserved: boolean }>;
  if (reserved[0]?.reserved !== true) {
    throw new AppError(429, 'budget_exceeded', 'Daily AI token budget exceeded.');
  }

  const content: Array<
    { type: 'text'; text: string } | { type: 'file'; mediaType: string; data: string }
  > = [{ type: 'text', text: options.prompt }];
  if (options.imageBase64) {
    content.push({ type: 'file', mediaType: 'image/png', data: options.imageBase64 });
  }

  let promptTokens = 0;
  let completionTokens = 0;
  let totalTokens = 0;

  try {
    const result = await generateText({
      model: google(env.AI_MODEL),
      messages: [{ role: 'user', content }],
      ...(options.system ? { system: options.system } : {}),
      output: Output.object({ schema: options.schema }),
    });

    const usage = result.usage;
    promptTokens = usage?.inputTokens ?? 0;
    completionTokens = usage?.outputTokens ?? 0;
    totalTokens = usage?.totalTokens ?? promptTokens + completionTokens;

    const parsed = options.schema.safeParse(result.output);
    if (!parsed.success) {
      logger.error('ai_invalid_response', { userId: options.userId, issues: parsed.error.issues });
      throw new AppError(502, 'ai_invalid_response', 'AI returned an unexpected format.');
    }
    if (totalTokens === 0 && !result.output) {
      throw new AppError(502, 'ai_empty_response', 'AI returned an empty response.');
    }
    return parsed.data;
  } catch (error) {
    if (error instanceof AppError) throw error;
    logger.error('ai_request_failed', {
      userId: options.userId,
      error: error instanceof Error ? error.message : String(error),
    });
    throw new AppError(502, 'ai_unavailable', 'AI provider is unavailable.');
  } finally {
    await db.execute(
      sql`select public.settle_llm_tokens(${options.userId}, ${RESERVATION_TOKENS}, ${totalTokens})`,
    );
    await db.insert(llmUsageLog).values({
      user_id: options.userId,
      model: env.AI_MODEL,
      prompt_tokens: promptTokens,
      completion_tokens: completionTokens,
      total_tokens: totalTokens,
    });
  }
}
