// Ref: BLUEPRIN.md & ux_doc.md
import React, { useState } from 'react';
import AppLayout from '../layout/AppLayout';
import ComponentCard from '../components/common/ComponentCard';

const JobApply = () => {
  const [step, setStep] = useState(1);

  return (
    <AppLayout>
      <div className="p-4 md:p-6 2xl:p-10">
        <ComponentCard title="Apply Flow">
          <div className="mb-8 flex items-center justify-center">
            {[1, 2, 3].map((s) => (
              <div key={s} className={`flex items-center ${s < 3 ? 'w-full' : ''}`}>
                <div className={`flex h-10 w-10 items-center justify-center rounded-full ${step >= s ? 'bg-primary text-white' : 'bg-stroke'}`}>
                  {s}
                </div>
                {s < 3 && <div className={`h-1 flex-grow ${step > s ? 'bg-primary' : 'bg-stroke'}`} />}
              </div>
            ))}
          </div>

          <div className="text-center">
            {step === 1 && <p>Upload Resume</p>}
            {step === 2 && <p>Confirm Details</p>}
            {step === 3 && <p>Application Submitted</p>}
          </div>

          <div className="mt-8 flex justify-between">
            <button disabled={step === 1} onClick={() => setStep(step - 1)} className="rounded bg-stroke px-6 py-2">Back</button>
            <button disabled={step === 3} onClick={() => setStep(step + 1)} className="rounded bg-primary px-6 py-2 text-white">Next</button>
          </div>
        </ComponentCard>
      </div>
    </AppLayout>
  );
};

export default JobApply;
