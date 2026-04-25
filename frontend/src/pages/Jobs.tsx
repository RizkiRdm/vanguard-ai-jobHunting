import { useState } from 'react';
import { Button } from '../components/ui/Button';
import { TaskTable } from '../components/agent/TaskTable';
import { useAgentTasks } from '../hooks/useAgentTasks';
import api from '../api';
import { useToast } from '../hooks/useToast';

export default function Jobs() {
  const [showForm, setShowForm] = useState(false);
  const [url, setUrl] = useState('');
  const { tasks, loading, refetch } = useAgentTasks();
  const toast = useToast();

  const startScrape = async () => {
    try {
      await api.post('/agent/scrape', { url });
      toast.success('Agent started!');
      setShowForm(false);
    } catch { toast.error('Failed to start agent'); }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold">Jobs</h1>
        <Button onClick={() => setShowForm(!showForm)}>Start Discovery</Button>
      </div>
      {showForm && (
        <div className="bg-surface p-4 rounded-xl border border-border space-y-2">
          <input className="w-full bg-elevated border border-border rounded px-3 py-2" placeholder="Job Portal URL" value={url} onChange={e => setUrl(e.target.value)} />
          <div className="flex gap-2">
            <Button onClick={startScrape}>Start Agent</Button>
            <Button variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
          </div>
        </div>
      )}
      <TaskTable tasks={tasks} loading={loading} onViewStream={() => {}} onStop={(id) => api.post(`/agent/tasks/${id}/stop`).then(refetch)} />
    </div>
  );
}
