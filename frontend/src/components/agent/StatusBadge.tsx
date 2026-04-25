import { TaskStatus } from '../../types';

export const StatusBadge = ({ status }: { status: TaskStatus }) => {
  const styles = {
    RUNNING: 'bg-green-500/10 text-green-400',
    AWAITING_USER: 'bg-amber-500/10 text-amber-400',
    QUEUED: 'bg-indigo-500/10 text-indigo-400',
    COMPLETED: 'bg-elevated text-text-muted',
    FAILED: 'bg-red-500/10 text-red-400',
  };
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium inline-flex items-center gap-1.5 ${styles[status]}`}>
      {status === 'RUNNING' && <span className='w-1.5 h-1.5 rounded-full bg-status-running animate-pulse' />}
      {status}
    </span>
  );
};
