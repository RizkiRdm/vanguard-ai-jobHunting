import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Briefcase, User, Settings, Shield } from 'lucide-react';

export const Sidebar = () => (
  <aside className="w-56 bg-surface border-r border-border h-screen flex flex-col">
    <div className="h-16 flex items-center px-6 gap-2 text-text-primary font-bold">
      <Shield className="w-6 h-6 text-accent" />
      Vanguard
    </div>
    <nav className="flex-1 px-3 py-4 space-y-1">
      {[
        { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
        { path: '/jobs', icon: Briefcase, label: 'Jobs' },
        { path: '/profile', icon: User, label: 'Profile' },
        { path: '/settings', icon: Settings, label: 'Settings' },
      ].map(({ path, icon: Icon, label }) => (
        <NavLink
          key={path}
          to={path}
          className={({ isActive }) =>
            `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              isActive ? 'bg-accent/10 text-accent' : 'text-text-secondary hover:bg-elevated hover:text-text-primary'
            }`
          }
        >
          <Icon className="w-5 h-5" />
          {label}
        </NavLink>
      ))}
    </nav>
    <div className="p-4 border-t border-border">
      <div className="flex items-center gap-2 text-xs text-text-muted">
        <div className="w-2 h-2 rounded-full bg-border" />
        Agent Idle
      </div>
    </div>
  </aside>
);
