import { useState, useRef, useEffect } from 'react';
import { AgentTask } from '../../types';
import { StatusBadge } from './StatusBadge';
import { Button } from '../ui/Button';
import { Skeleton } from '../ui/Skeleton';
import api from '../../api';

export const AgentStreamPanel = ({ task, onClose }: { task: AgentTask | null, onClose: () => void }) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [answer, setAnswer] = useState('');
  useEffect(() => scrollRef.current?.scrollIntoView({ behavior: 'smooth' }), [task?.metadata.logs]);
  if (!task) return null;
  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="w-[480px] bg-surface border-l border-border h-full flex flex-col relative z-10">
        <div className="h-14 flex items-center justify-between px-5 border-b border-border">
          <span className="font-mono text-sm">Stream {task.id.slice(0, 8)}</span>
          <div className="flex items-center gap-3">
            <StatusBadge status={task.status} />
            <Button variant="ghost" onClick={onClose}>✕</Button>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-1 font-mono text-xs">
          {task.metadata.logs?.map((l, i) => (
            <div key={i} className={l.type === 'ERROR' ? 'text-status-failed' : l.type === 'ACTION' ? 'text-accent' : l.type === 'OBSERVE' ? 'text-status-running' : 'text-text-secondary'}>
              [{l.type}] {l.message}
            </div>
          ))}
          <div ref={scrollRef} />
        </div>
        {task.status === 'AWAITING_USER' && (
          <div className="p-4 border-t border-border bg-amber-500/5">
            <p className="text-sm mb-2 text-amber-400">{task.metadata.subjective_question}</p>
            <textarea className="w-full bg-elevated border border-border rounded p-2 text-sm mb-2" value={answer} onChange={e => setAnswer(e.target.value)} />
            <Button onClick={() => api.post(`/agent/interact/${task.id}`, { answer })}>Send Answer</Button>
          </div>
        )}
      </div>
    </div>
  );
};
