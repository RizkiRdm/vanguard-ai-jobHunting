import type { Page } from 'playwright';
import { logger } from '../../lib/logger.ts';

export interface JobCandidate {
  title: string;
  company: string | null;
  location: string | null;
  url: string;
  snippet: string | null;
}

const DEFAULT_SEARCH_ENDPOINT = 'https://duckduckgo.com/html/';

/**
 * Search engines used for discovery. Canonical duckduckgo.com/html/ is preferred
 * because html.duckduckgo.com intermittently triggers TLS common name errors.
 * Fallback to secondary endpoint if primary navigation fails.
 */
export const SEARCH_ENDPOINTS = [
  DEFAULT_SEARCH_ENDPOINT,
  'https://html.duckduckgo.com/html/',
] as const;

export function unwrapRedirect(href: string, baseUrl: string = DEFAULT_SEARCH_ENDPOINT): string {
  try {
    const url = new URL(href, baseUrl);
    const target = url.searchParams.get('uddg');
    return target ? decodeURIComponent(target) : href;
  } catch {
    return href;
  }
}

export async function searchJobs(
  page: Page,
  query: string,
  limit: number,
  endpoints: readonly string[] = SEARCH_ENDPOINTS,
): Promise<JobCandidate[]> {
  let lastError: Error | null = null;
  let activeEndpoint: string | null = null;

  for (const endpoint of endpoints) {
    try {
      const searchUrl = new URL(endpoint);
      searchUrl.searchParams.set('q', query);
      await page.goto(searchUrl.toString(), { waitUntil: 'domcontentloaded' });
      activeEndpoint = endpoint;
      break;
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      logger.warn('discovery_navigation_failed', {
        endpoint,
        error: lastError.message,
      });
    }
  }

  if (!activeEndpoint) {
    throw lastError ?? new Error('Discovery navigation failed across all endpoints');
  }

  const raw = await page.$$eval('a.result__a', (elements) =>
    elements.map((el) => ({
      title: (el.textContent ?? '').trim(),
      href: (el as HTMLAnchorElement).href,
    })),
  );

  const snippets = await page.$$eval('.result__snippet', (elements) =>
    elements.map((el) => (el.textContent ?? '').trim()),
  );

  const jobs: JobCandidate[] = [];
  for (const [index, entry] of raw.entries()) {
    if (!entry.title || !entry.href) continue;
    const url = unwrapRedirect(entry.href, activeEndpoint);
    if (!url.startsWith('http')) continue;
    jobs.push({
      title: entry.title,
      company: null,
      location: null,
      url,
      snippet: snippets[index] ?? null,
    });
    if (jobs.length >= limit) break;
  }
  return jobs;
}
