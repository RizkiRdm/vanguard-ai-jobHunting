import { describe, expect, it } from 'vitest';
import { AiDecision, ResumeProfileExtraction } from './prompts.ts';

describe('AiDecision', () => {
  it('accepts a well-formed action', () => {
    const parsed = AiDecision.parse({
      action: 'fill',
      selector: '#email',
      value: 'me@example.com',
      thought: 'Fill the email field',
    });
    expect(parsed.action).toBe('fill');
  });

  it('rejects unknown actions, including submit attempts', () => {
    expect(AiDecision.safeParse({ action: 'click' }).success).toBe(true);
    expect(AiDecision.safeParse({ action: 'submit' }).success).toBe(false);
  });

  it('rejects oversized selectors', () => {
    expect(AiDecision.safeParse({ action: 'click', selector: 'x'.repeat(501) }).success).toBe(
      false,
    );
  });
});

describe('ResumeProfileExtraction', () => {
  it('parses valid profile extraction data', () => {
    const valid = {
      full_name: 'Alex Mercer',
      email: 'alex@example.com',
      phone: '+1-555-0199',
      summary: 'Senior software engineer with 8 years of experience building distributed systems.',
      target_role: 'Staff Software Engineer',
      expected_salary: '$180,000 - $210,000',
      skills: ['TypeScript', 'Node.js', 'PostgreSQL', 'Cloudflare Workers'],
      experience_years: 8,
      location: 'San Francisco, CA',
    };
    const result = ResumeProfileExtraction.safeParse(valid);
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.full_name).toBe('Alex Mercer');
      expect(result.data.skills).toHaveLength(4);
      expect(result.data.experience_years).toBe(8);
    }
  });

  it('allows empty/partial extraction when resume misses fields', () => {
    const partial = {
      full_name: 'Jane Doe',
      skills: ['Rust'],
    };
    const result = ResumeProfileExtraction.safeParse(partial);
    expect(result.success).toBe(true);
  });

  it('rejects invalid email formats', () => {
    const invalid = {
      email: 'not-an-email',
    };
    const result = ResumeProfileExtraction.safeParse(invalid);
    expect(result.success).toBe(false);
  });
});
