import { useState, useEffect, useCallback } from 'react';
import { AgentTask } from '../types';
import api from '../api';

export const useAgentTasks = () => {
  const [tasks, setTasks] = useState<AgentTask[]>([]);
  const [loading, setLoading] = useState(true);
  const refetch = useCallback(async () => {
    try {
      const res = await api.get('/agent/tasks');
      setTasks(res.data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => { refetch(); const i = setInterval(refetch, 10000); return () => clearInterval(i); }, [refetch]);
  return { tasks, loading, refetch };
};
