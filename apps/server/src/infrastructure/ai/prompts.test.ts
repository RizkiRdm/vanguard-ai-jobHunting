import { describe, expect, it } from 'vitest';
import { AiDecision } from './prompts.ts';

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
