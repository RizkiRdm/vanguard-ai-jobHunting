// Ref: BLUEPRIN.md & ux_doc.md
import React from 'react';
import AppLayout from '../layout/AppLayout';
import ComponentCard from '../components/common/ComponentCard';

const JobList = () => {
  const jobs = [
    { id: 1, title: 'Senior Backend Dev', company: 'TechCorp', status: 'Applied' },
    { id: 2, title: 'Frontend Engineer', company: 'WebSolutions', status: 'Pending' },
  ];

  return (
    <AppLayout>
      <div className="p-4 md:p-6 2xl:p-10">
        <ComponentCard title="Available Jobs">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-stroke">
                <th className="py-3 px-4">Title</th>
                <th className="py-3 px-4">Company</th>
                <th className="py-3 px-4">Status</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map(job => (
                <tr key={job.id} className="border-b border-stroke">
                  <td className="py-3 px-4 font-medium text-black dark:text-white">{job.title}</td>
                  <td className="py-3 px-4">{job.company}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 rounded text-xs ${job.status === 'Applied' ? 'bg-success text-white' : 'bg-warning text-white'}`}>
                      {job.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </ComponentCard>
      </div>
    </AppLayout>
  );
};

export default JobList;
