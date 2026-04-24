// Ref: BLUEPRIN.md & ux_doc.md
import React from 'react';
import AppLayout from '../layout/AppLayout';
import ComponentCard from '../components/common/ComponentCard';

const Screenshots = () => {
  const images = [
    { id: 1, title: 'Task #8821 Start', src: '/images/product/task-1.jpg' },
    { id: 2, title: 'Task #8821 Apply', src: '/images/product/task-2.jpg' },
  ];

  return (
    <AppLayout>
      <div className="p-4 md:p-6 2xl:p-10">
        <ComponentCard title="Agent Screenshots">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {images.map(img => (
              <div key={img.id} className="border border-stroke p-2 dark:border-strokedark">
                <img src={img.src} alt={img.title} className="w-full h-auto mb-2" />
                <p className="text-center font-medium">{img.title}</p>
              </div>
            ))}
          </div>
        </ComponentCard>
      </div>
    </AppLayout>
  );
};

export default Screenshots;
