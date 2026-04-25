import { AgentTask } from '../../types';
import { StatusBadge } from './StatusBadge';
import { Button } from '../ui/Button';
import { SkeletonRow } from '../ui/Skeleton';

export const TaskTable = ({ tasks, loading, onViewStream, onStop }: { tasks: AgentTask[], loading: boolean, onViewStream: (t: AgentTask) => void, onStop: (id: string) => void }) => {
  if (loading) return <div>{[...Array(4)].map((_, i) => <SkeletonRow key={i} />)}</div>;
  if (tasks.length === 0) return <div className="text-center p-8 text-text-muted">No tasks yet. Start an agent to begin.</div>;
  return (
    <div className="w-full bg-surface border border-border rounded-xl overflow-hidden">
      <div className="bg-elevated p-3 text-xs uppercase tracking-widest text-text-muted flex">
        <span className="w-24">ID</span><span className="flex-1">Type</span><span className="w-32">Status</span><span className="w-32">Created</span><span className="w-24">Actions</span>
      </div>
      {tasks.map(t => (
        <div key={t.id} className="flex items-center p-3 border-t border-border text-sm">
          <span className="w-24 font-mono text-xs">{t.id.slice(0, 8)}</span>
          <span className="flex-1 text-text-secondary">{t.type}</span>
          <span className="w-32"><StatusBadge status={t.status} /></span>
          <span className="w-32 text-text-muted text-xs">{new Date(t.created_at).toLocaleDateString()}</span>
          <span className="w-24 flex gap-2">
            <Button size="sm" variant="ghost" onClick={() => onViewStream(t)}>View</Button>
            {t.status === 'RUNNING' && <Button size="sm" variant="danger" onClick={() => onStop(t.id)}>Stop</Button>}
          </span>
        </div>
      ))}
    </div>
  );
};
