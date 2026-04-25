import { Briefcase, Search, Zap } from 'lucide-react';
import { StatCard } from '../components/dashboard/StatCard';
import { SkeletonCard } from '../components/ui/Skeleton';
import { useProfile } from '../hooks/useProfile';

export default function Dashboard() {
  const { profile, loading } = useProfile();
  if (loading) return <div className="grid grid-cols-3 gap-4"><SkeletonCard /><SkeletonCard /><SkeletonCard /></div>;
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-4">
        <StatCard label="Jobs Applied" value={profile?.stats.total_applied || 0} icon={<Briefcase />} />
        <StatCard label="Jobs Discovered" value={profile?.stats.total_discovered || 0} icon={<Search />} />
        <StatCard label="Tokens Used" value={profile?.stats.token_cost || 0} icon={<Zap />} />
      </div>
      <div className="text-sm font-semibold uppercase tracking-widest text-text-muted">Active Tasks</div>
    </div>
  );
}
