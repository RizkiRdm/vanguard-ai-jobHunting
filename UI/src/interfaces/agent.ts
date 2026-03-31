export type TaskStatus = 'QUEUED' | 'RUNNING' | 'AWAITING_USER' | 'COMPLETED' | 'FAILED';
export type TaskType = 'DISCOVERY' | 'AUTOMATED_APPLY';

export interface AgentTask {
    id: string;
    user_id: string;
    task_type: TaskType;
    status: TaskStatus;
    metadata: {
        target_url?: string;
        job_title?: string;
        company?: string;
        thought?: string;
        action?: string;
        screenshot_url?: string;
        reason?: string;
        user_answer?: unknown;
    };
    created_at: string;
}

export interface LLMUsage {
    total_tokens: number;
    daily_budget_limit: number;
    cost_estimate: number;
}