// Ref: BLUEPRIN.md & ux_doc.md
import React, { useEffect, useState } from 'react';
import AppLayout from '../layout/AppLayout';
import ComponentCard from '../components/common/ComponentCard';

interface DashboardStats {
  applied: number;
  tokens: number;
}

const Dashboard = () => {
  const [stats, setStats] = useState<DashboardStats>({ applied: 0, tokens: 0 });

  useEffect(() => {
    setStats({ applied: 142, tokens: 45000 });
  }, []);

  return (
    <AppLayout>

    </AppLayout>
  );
};

export default Dashboard;
