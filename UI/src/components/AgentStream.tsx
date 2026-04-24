// Ref: BLUEPRIN.md & ux_doc.md
import React from 'react';
import ComponentCard from './common/ComponentCard';

interface AgentStreamProps {
  task_id: string;
  thought: string;
  action: string;
  screenshot_url?: string;
  onSendHelp: (answer: string) => void;
}

const AgentStream: React.FC<AgentStreamProps> = ({ task_id, thought, action, screenshot_url, onSendHelp }) => {
  const [answer, setAnswer] = React.useState('');

  return (
    <ComponentCard title={`AGENT STREAM - Task #${task_id}`}>
      <div className="flex flex-col gap-4">
        <div className="bg-gray-100 p-3 rounded text-sm dark:bg-meta-4">
          <p className="font-semibold text-primary">Thought:</p>
          <p className="text-bodydark1">{thought}</p>
        </div>
        <div className="bg-gray-100 p-3 rounded text-sm dark:bg-meta-4">
          <p className="font-semibold text-primary">Action:</p>
          <p className="text-bodydark1">{action}</p>
        </div>
        
        {screenshot_url && (
            <div className="border border-stroke dark:border-strokedark p-1">
                <img src={screenshot_url} alt="Latest Agent Screenshot" className="w-full h-auto" />
            </div>
        )}

        <div className="border-t border-stroke pt-4 dark:border-strokedark">
            <p className="text-sm font-bold text-red-500 mb-2">(!) AGENT NEEDS HELP:</p>
            <textarea 
                className="w-full rounded border border-stroke bg-transparent p-3 outline-none focus:border-primary dark:border-strokedark dark:bg-meta-4"
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                placeholder="Provide answer here..."
            />
            <button 
                onClick={() => onSendHelp(answer)}
                className="mt-2 w-full rounded bg-primary px-6 py-2 font-medium text-white hover:bg-opacity-90"
            >
                Send
            </button>
        </div>
      </div>
    </ComponentCard>
  );
};

export default AgentStream;
