import { chmod, mkdir, readFile, writeFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { chromium, type BrowserContext, type Page } from 'playwright';
import { getEnv } from '../../config/env.ts';
import { logger } from '../../lib/logger.ts';

const STATE_DIR = resolve(process.cwd(), '.browser-state');

export interface BrowserSession {
  page: Page;
  context: BrowserContext;
  saveState: () => Promise<void>;
  close: () => Promise<void>;
}

async function statePath(userId: string): Promise<string> {
  await mkdir(STATE_DIR, { recursive: true, mode: 0o700 });
  return join(STATE_DIR, `${userId}.json`);
}

/**
 * Loads a stored browser session for the user (cookies, local storage).
 * State files are per-user, never shared, and never served over HTTP.
 */
async function loadState(userId: string) {
  try {
    const raw = await readFile(await statePath(userId), 'utf8');
    return JSON.parse(raw);
  } catch {
    return undefined;
  }
}

async function saveState(userId: string, context: BrowserContext): Promise<void> {
  try {
    const state = await context.storageState();
    const path = await statePath(userId);
    await writeFile(path, JSON.stringify(state), { mode: 0o600 });
    await chmod(path, 0o600);
  } catch (error) {
    logger.warn('browser_state_save_failed', {
      userId,
      error: error instanceof Error ? error.message : String(error),
    });
  }
}

/**
 * Opens an isolated browser context for one task.
 *
 * Each task gets its own context, so one user's session can never be reused for
 * another user. Playwright talks over its own pipe - no remote debugging port or
 * CDP endpoint is ever exposed.
 */
export async function openSession(userId: string): Promise<BrowserSession> {
  const env = getEnv();
  const browser = await chromium.launch({
    headless: env.BROWSER_HEADLESS,
    args: ['--no-sandbox', '--disable-dev-shm-usage'],
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    acceptDownloads: false,
    storageState: await loadState(userId),
  });
  context.setDefaultTimeout(env.BROWSER_TIMEOUT_MS);

  const page = await context.newPage();

  return {
    page,
    context,
    saveState: () => saveState(userId, context),
    close: async () => {
      await context.close().catch(() => undefined);
      await browser.close().catch(() => undefined);
    },
  };
}
