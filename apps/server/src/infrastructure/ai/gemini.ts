import { GoogleGenAI } from '@google/genai';
import type { z } from 'zod';
import { getEnv } from '../../config/env.ts';
import { getDb } from '../../lib/db.ts';
import { logger } from '../../lib/logger.ts';
import { AppError } from '../../lib/errors.ts';

/** Tokens reserved before a call so concurrent requests cannot overspend the cap. */
const RESERVATION_TOKENS = 4_000;

let client: GoogleGenAI | undefined;

function getClient(): GoogleGenAI {
  if (!client) {
    client = new GoogleGenAI({ apiKey: getEnv().GEMINI_API_KEY });
  }
  return client;
}

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
  const sql = getDb();

  const reserved = await sql<{ reserve_llm_tokens: boolean }[]>`
    select public.reserve_llm_tokens(
      ${options.userId},
      ${RESERVATION_TOKENS},
      ${env.DAILY_TOKEN_BUDGET}
    ) as reserve_llm_tokens
  `;
  if (reserved[0]?.reserve_llm_tokens !== true) {
    throw new AppError(429, 'budget_exceeded', 'Daily AI token budget exceeded.');
  }

  const parts: Array<Record<string, unknown>> = [{ text: options.prompt }];
  if (options.imageBase64) {
    parts.push({ inlineData: { mimeType: 'image/png', data: options.imageBase64 } });
  }

  let promptTokens = 0;
  let completionTokens = 0;
  let totalTokens = 0;

  try {
    const response = await getClient().models.generateContent({
      model: env.AI_MODEL,
      contents: [{ role: 'user', parts }],
      config: {
        responseMimeType: 'application/json',
        ...(options.system ? { systemInstruction: options.system } : {}),
      },
    });

    const usage = response.usageMetadata;
    promptTokens = usage?.promptTokenCount ?? 0;
    completionTokens = usage?.candidatesTokenCount ?? 0;
    totalTokens = usage?.totalTokenCount ?? promptTokens + completionTokens;

    const text = response.text;
    if (!text) throw new AppError(502, 'ai_empty_response', 'AI returned an empty response.');

    const parsed = options.schema.safeParse(JSON.parse(text));
    if (!parsed.success) {
      logger.error('ai_invalid_response', { userId: options.userId, issues: parsed.error.issues });
      throw new AppError(502, 'ai_invalid_response', 'AI returned an unexpected format.');
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
    await sql`select public.settle_llm_tokens(${options.userId}, ${RESERVATION_TOKENS}, ${totalTokens})`;
    await sql`
      insert into public.llm_usage_log (user_id, model, prompt_tokens, completion_tokens, total_tokens)
      values (${options.userId}, ${env.AI_MODEL}, ${promptTokens}, ${completionTokens}, ${totalTokens})
    `;
  }
}
