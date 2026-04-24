// Ref: BLUEPRIN.md & ux_doc.md
import React, { useEffect, useState } from 'react';
import AppLayout from '../layout/AppLayout';
import ComponentCard from '../components/common/ComponentCard';
import AgentStream from '../components/AgentStream';

interface Task {
  id: string;
  type: string;
  status: string;
}

const Dashboard = () => {
  const [showStream, setShowStream] = useState(false);
  const [tasks, setTasks] = useState<Task[]>([]);

  useEffect(() => {
    // Mocking data as per UX_doc.md
    setTasks([
        { id: '8821...', type: 'APPLY', status: 'RUNNING' },
        { id: '712a...', type: 'DISCOVERY', status: 'COMPLETED' }
    ]);
  }, []);

  return (
    <AppLayout>
      <div className="p-4 md:p-6 2xl:p-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <ComponentCard title="Active Resume">
            <p className="text-sm text-body dark:text-bodydark mb-4">File: MyCV_2024.pdf</p>
            <button className="rounded bg-primary px-6 py-2 font-medium text-white hover:bg-opacity-90">Change Resume</button>
          </ComponentCard>
          <ComponentCard title="Bot Statistics">
            <div className="flex gap-4">
                <div className="text-center flex-1 py-2 border-r border-stroke">
                    <p className="text-sm">Applied</p>
                    <p className="text-xl font-bold text-primary">142</p>
                </div>
                <div className="text-center flex-1 py-2">
                    <p className="text-sm">Tokens</p>
                    <p className="text-xl font-bold text-primary">45k</p>
                </div>
            </div>
          </ComponentCard>
        </div>

        <ComponentCard title="Current Tasks">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-stroke">
                <th className="py-2">ID</th>
                <th className="py-2">TYPE</th>
                <th className="py-2">STATUS</th>
                <th className="py-2">ACTION</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map(t => (
                <tr key={t.id} className="border-b border-stroke">
                  <td className="py-3">{t.id}</td>
                  <td className="py-3">{t.type}</td>
                  <td className="py-3">{t.status}</td>
                  <td className="py-3">
                    <button onClick={() => setShowStream(true)} className="text-primary hover:underline">View Stream</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </ComponentCard>

        {showStream && (
            <div className="fixed top-20 right-6 w-96 shadow-lg z-50">
                <AgentStream 
                    task_id="8821" 
                    thought="Clicking Easy Apply" 
                    action="CLICK button" 
                    onSendHelp={(a) => console.log(a)} 
                />
            </div>
        )}
      </div>
    </AppLayout>
  );
};

export default Dashboard;
