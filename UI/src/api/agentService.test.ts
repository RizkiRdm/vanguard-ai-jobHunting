import { describe, it, expect, vi } from 'vitest';
import api from './client';
import { agentService } from './agentService';

// Mock axios client
vi.mock('./client', () => ({
    default: {
        post: vi.fn(),
        get: vi.fn(),
    },
}));

describe('agentService', () => {
    it('triggerScrape harus memanggil endpoint /agent/scrape dengan method POST', async () => {
        await agentService.triggerScrape();
        expect(api.post).toHaveBeenCalledWith('/agent/scrape');
    });

    it('submitAnswer harus mengirim payload ke task_id yang benar', async () => {
        const taskId = '123';
        const mockAnswer = { salary: '5000' };

        await agentService.submitAnswer(taskId, mockAnswer);
        expect(api.post).toHaveBeenCalledWith(`/agent/interact/${taskId}`, { answer: mockAnswer });
    });
});