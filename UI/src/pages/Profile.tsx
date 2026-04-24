// Ref: BLUEPRIN.md & ux_doc.md
import React from 'react';
import AppLayout from '../layout/AppLayout';
import ComponentCard from '../components/common/ComponentCard';

const Profile = () => {
  return (
    <AppLayout>
      <div className="p-4 md:p-6 2xl:p-10">
        <ComponentCard title="Profile Management">
          <form className="space-y-4">
            <div>
              <label className="mb-2.5 block text-black dark:text-white">Full Name</label>
              <input type="text" className="w-full rounded border border-stroke bg-transparent py-3 px-5 outline-none focus:border-primary dark:border-strokedark" defaultValue="User Name" />
            </div>
            <div>
              <label className="mb-2.5 block text-black dark:text-white">Email</label>
              <input type="email" className="w-full rounded border border-stroke bg-transparent py-3 px-5 outline-none focus:border-primary dark:border-strokedark" defaultValue="user@email.com" />
            </div>
            <button className="flex justify-center rounded bg-primary px-6 py-2 font-medium text-white hover:bg-opacity-90">
              Save Profile
            </button>
          </form>
        </ComponentCard>
      </div>
    </AppLayout>
  );
};

export default Profile;
