export const StatCard = ({ label, value, icon: Icon }: { label: string, value: string | number, icon?: React.ReactNode }) => (
  <div className="bg-surface border border-border rounded-xl p-5">
    {Icon && <div className="text-text-muted mb-3">{Icon}</div>}
    <div className="text-3xl font-semibold text-text-primary">{value}</div>
    <div className="text-xs uppercase tracking-widest text-text-muted mt-1">{label}</div>
  </div>
);
