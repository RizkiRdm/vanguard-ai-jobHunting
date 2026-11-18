import type { Page } from 'playwright';
import { describe, expect, it, vi } from 'vitest';
import { SEARCH_ENDPOINTS, searchJobs, unwrapRedirect } from './discovery.ts';

describe('discovery', () => {
  describe('unwrapRedirect', () => {
    it('decodes uddg parameter correctly', () => {
      const target = 'https://example.com/jobs/123';
      const encoded = encodeURIComponent(target);
      const href = `/l/?uddg=${encoded}&routine=1`;
      expect(unwrapRedirect(href, 'https://duckduckgo.com/html/')).toBe(target);
    });

    it('returns raw href if uddg is absent', () => {
      const href = 'https://example.com/direct';
      expect(unwrapRedirect(href)).toBe(href);
    });

    it('handles malformed urls gracefully', () => {
      const invalid = ':::not-a-url:::';
      expect(unwrapRedirect(invalid)).toBe(invalid);
    });
  });

  describe('searchJobs', () => {
    it('navigates to canonical endpoint first and parses jobs', async () => {
      const visitedUrls: string[] = [];
      const mockPage = {
        goto: vi.fn(async (url: string) => {
          visitedUrls.push(url);
          return null;
        }),
        $$eval: vi.fn(async (selector: string) => {
          if (selector === 'a.result__a') {
            return [
              { title: 'Software Engineer', href: '/l/?uddg=https%3A%2F%2Fjob.com%2F1' },
              { title: 'Frontend Developer', href: '/l/?uddg=https%3A%2F%2Fjob.com%2F2' },
            ];
          }
          if (selector === '.result__snippet') {
            return ['Build great things', 'Write clean code'];
          }
          return [];
        }),
      } as unknown as Page;

      const jobs = await searchJobs(mockPage, 'engineer remote', 1);

      expect(visitedUrls[0]).toBe('https://duckduckgo.com/html/?q=engineer+remote');
      expect(jobs).toHaveLength(1);
      expect(jobs[0]).toEqual({
        title: 'Software Engineer',
        company: null,
        location: null,
        url: 'https://job.com/1',
        snippet: 'Build great things',
      });
    });

    it('retries fallback endpoint when primary navigation encounters cert error', async () => {
      const visitedUrls: string[] = [];
      const mockPage = {
        goto: vi.fn(async (url: string) => {
          visitedUrls.push(url);
          if (url.startsWith(SEARCH_ENDPOINTS[0])) {
            throw new Error('net::ERR_CERT_COMMON_NAME_INVALID at https://duckduckgo.com/html/');
          }
          return null;
        }),
        $$eval: vi.fn(async (selector: string) => {
          if (selector === 'a.result__a') {
            return [{ title: 'Fallback Job', href: 'https://fallback.com/job' }];
          }
          if (selector === '.result__snippet') {
            return ['Snippet from fallback'];
          }
          return [];
        }),
      } as unknown as Page;

      const jobs = await searchJobs(mockPage, 'devops', 10);

      expect(visitedUrls).toHaveLength(2);
      expect(visitedUrls[0]).toContain(SEARCH_ENDPOINTS[0]);
      expect(visitedUrls[1]).toContain(SEARCH_ENDPOINTS[1]);
      expect(jobs).toHaveLength(1);
      expect(jobs[0]?.title).toBe('Fallback Job');
    });

    it('throws error if all endpoints fail to navigate', async () => {
      const mockPage = {
        goto: vi.fn(async () => {
          throw new Error('net::ERR_CONNECTION_REFUSED');
        }),
      } as unknown as Page;

      await expect(searchJobs(mockPage, 'fail', 5)).rejects.toThrow('net::ERR_CONNECTION_REFUSED');
    });
  });
});
