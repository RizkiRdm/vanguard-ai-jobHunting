import { describe, it, expect, beforeEach } from 'vitest';
import { useAgentStore } from './useAgentStore';
import type { AgentTask } from '../interfaces/agent';

describe('useAgentStore', () => {
    // Reset store sebelum setiap test
    beforeEach(() => {
        useAgentStore.setState({ tasks: [], activeTask: null });
    });

    it('harus bisa menyimpan daftar task (setTasks)', () => {
        const mockTasks: AgentTask[] = [
            { id: '1', status: 'QUEUED', task_type: 'DISCOVERY', metadata: {}, created_at: '', user_id: 'u1' }
        ];

        useAgentStore.getState().setTasks(mockTasks);
        expect(useAgentStore.getState().tasks).toHaveLength(1);
        expect(useAgentStore.getState().tasks[0].id).toBe('1');
    });

    it('harus mengupdate metadata activeTask saat menerima stream payload yang cocok', () => {
        const initialTask: AgentTask = {
            id: 'task_123',
            status: 'RUNNING',
            task_type: 'AUTOMATED_APPLY',
            metadata: { thought: 'Initial' },
            created_at: '',
            user_id: 'u1'
        };

        // Set task aktif
        useAgentStore.setState({ activeTask: initialTask });

        // Simulasi Payload WebSocket
        const payload = {
            task_id: 'task_123',
            thought: 'I am clicking the apply button',
            action: 'CLICK'
        };

        useAgentStore.getState().updateTaskStream(payload);

        const updatedTask = useAgentStore.getState().activeTask;
        expect(updatedTask?.metadata.thought).toBe('I am clicking the apply button'); //
        expect(updatedTask?.metadata.action).toBe('CLICK'); //
    });

    it('TIDAK boleh mengupdate activeTask jika task_id tidak cocok', () => {
        const initialTask: AgentTask = {
            id: 'task_123',
            status: 'RUNNING',
            task_type: 'AUTOMATED_APPLY',
            metadata: { thought: 'Stay the same' },
            created_at: '',
            user_id: 'u1'
        };

        useAgentStore.setState({ activeTask: initialTask });

        const payload = {
            task_id: 'different_id',
            thought: 'This should not update'
        };

        useAgentStore.getState().updateTaskStream(payload);
        expect(useAgentStore.getState().activeTask?.metadata.thought).toBe('Stay the same'); //
    });
});