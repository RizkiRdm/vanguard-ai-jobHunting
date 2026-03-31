import api from './client';
import type { AgentTask } from '../interfaces/agent';

export const agentService = {
    triggerScrape: () => api.post<{ task_id: string }>('/agent/scrape'),

    getTasks: () => api.get<AgentTask[]>('/agent/tasks'),

    submitAnswer: (taskId: string, answer: unknown) =>
        api.post(`/agent/interact/${taskId}`, { answer }),

    stopTask: (taskId: string) => api.post(`/agent/tasks/${taskId}/stop`),
};