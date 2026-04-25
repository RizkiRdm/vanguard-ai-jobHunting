export type TaskStatus = 'QUEUED' | 'RUNNING' | 'AWAITING_USER' | 'COMPLETED' | 'FAILED';
export type TaskType = 'DISCOVERY' | 'APPLY';

export interface AgentTask {
  id: string;
  type: TaskType;
  status: TaskStatus;
  created_at: string;
  metadata: {
    thought?: string;
    action?: string;
    subjective_question?: string;
    human_answer?: string;
    logs?: Array<{ type: 'THOUGHT' | 'ACTION' | 'OBSERVE' | 'ERROR'; message: string; ts: string }>;
  };
}

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  resume_filename?: string;
  stats: {
    total_applied: number;
    total_discovered: number;
    token_cost: number;
  };
}
