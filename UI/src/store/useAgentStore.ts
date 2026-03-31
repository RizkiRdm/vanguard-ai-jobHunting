import { create } from 'zustand';
import type { AgentTask } from '../interfaces/agent';

interface StreamPayload {
    task_id: string;
    thought?: string;
    action?: string;
    screenshot_url?: string;
    step?: number;
    [key: string]: unknown;
}

interface AgentState {
    tasks: AgentTask[];
    activeTask: AgentTask | null;
    setTasks: (tasks: AgentTask[]) => void;
    setActiveTask: (task: AgentTask | null) => void;
    updateTaskStream: (payload: StreamPayload) => void;
}

export const useAgentStore = create<AgentState>((set) => ({
    tasks: [],
    activeTask: null,

    setTasks: (tasks) => set({ tasks }),

    setActiveTask: (task) => set({ activeTask: task }),

    updateTaskStream: (payload) => set((state) => {
        if (!state.activeTask || state.activeTask.id !== payload.task_id) {
            return state;
        }

        const updatedActiveTask: AgentTask = {
            ...state.activeTask,
            metadata: {
                ...state.activeTask.metadata,
                ...payload // Menggabungkan thought, action, dll ke metadata
            }
        };

        return {
            activeTask: updatedActiveTask
        };
    }),
}));