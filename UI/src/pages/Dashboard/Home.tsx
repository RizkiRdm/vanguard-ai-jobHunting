import React from 'react';
import EcommerceMetrics from '../../components/ecommerce/EcommerceMetrics';
import BasicTableOne from '../../components/tables/BasicTables/BasicTableOne';
import { useProfileStore } from '../../store/useProfileStore';
import { useAgentStore } from '../../store/useAgentStore';

const Home: React.FC = () => {
  const profile = useProfileStore((state) => state.profile);
  const tasks = useAgentStore((state) => state.tasks);

  return (
    <>
      {/* Menggunakan komponen asli TailAdmin dari folder components/ecommerce */}
      <EcommerceMetrics />

      <div className="mt-4 grid grid-cols-12 gap-4 md:mt-6 md:gap-6 2xl:mt-7.5 2xl:gap-7.5">

        {/* ACTIVE RESUME CARD - Custom styling mengikuti tema TailAdmin */}
        <div className="col-span-12 rounded-sm border border-stroke bg-white py-6 px-7.5 shadow-default dark:border-strokedark dark:bg-boxdark xl:col-span-4">
          <h4 className="mb-2 text-xl font-semibold text-shadow-black dark:text-shadow-white">
            Active Resume
          </h4>
          <div className="flex items-center gap-3">
            <div className="flex h-11.5 w-11.5 items-center justify-center rounded-full bg-mauve-50 dark:bg-mauve-800">
              {/* Icon PDF/File sederhana */}
              <svg className="fill-blue-950 dark:fill-blue-light-50" width="18" height="18" viewBox="0 0 18 18">
                <path d="M15 0H3C1.35 0 0 1.35 0 3V15C0 16.65 1.35 18 3 18H15C16.65 18 18 16.65 18 15V3C18 1.35 16.65 0 15 0ZM11.25 13.5H3.75V12H11.25V13.5ZM14.25 10.5H3.75V9H14.25V10.5ZM14.25 7.5H3.75V6H14.25V7.5Z" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium">Current File</p>
              <h4 className="text-sm font-bold text-shadow-blackk dark:text-shadow-whitete truncate w-40">
                {profile?.resume_url?.split('/').pop() || 'No resume uploaded'}
              </h4>
            </div>
          </div>
          <button className="mt-6 flex w-full justify-center rounded bg-primary p-3 font-medium text-gray hover:bg-opacity-90">
            Upload New Resume
          </button>
        </div>

        {/* CURRENT TASKS TABLE */}
        <div className="col-span-12 xl:col-span-8">
          <BasicTableOne />

          {/* Debug info untuk menghilangkan error 'tasks' unused */}
          {tasks.length === 0 && (
            <p className="mt-4 text-center text-sm text-gray-500">No active agent tasks found.</p>
          )}
        </div>
      </div>
    </>
  );
};

export default Home;