import type { Page } from 'playwright';

export interface JobCandidate {
  title: string;
  company: string | null;
  location: string | null;
  url: string;
  snippet: string | null;
}

/**
 * Search engine used for discovery. The HTML endpoint needs no API key and
 * returns plain links, which keeps discovery honest: only links that are really
 * on the page can become jobs.
 */
const SEARCH_URL = 'https://html.duckduckgo.com/html/';

function unwrapRedirect(href: string): string {
  try {
    const url = new URL(href, SEARCH_URL);
    const target = url.searchParams.get('uddg');
    return target ? decodeURIComponent(target) : url.toString();
  } catch {
    return href;
  }
}

export async function searchJobs(
  page: Page,
  query: string,
  limit: number,
): Promise<JobCandidate[]> {
  const searchUrl = `${SEARCH_URL}?q=${encodeURIComponent(query)}`;
  await page.goto(searchUrl, { waitUntil: 'domcontentloaded' });

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
    const url = unwrapRedirect(entry.href);
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
