import { useState } from 'react';
import { Upload, CheckCircle, AlertCircle } from 'lucide-react';
import api from '../../api';

export const ResumeUpload = ({ onSuccess }: { onSuccess: () => void }) => {
  const [status, setStatus] = useState<'idle' | 'dragging' | 'uploading' | 'done' | 'error'>('idle');
  const upload = async (file: File) => {
    setStatus('uploading');
    const formData = new FormData();
    formData.append('file', file);
    try {
      await api.post('/profile/resume', formData);
      setStatus('done');
      onSuccess();
    } catch { setStatus('error'); }
  };
  return (
    <div onDragOver={(e) => { e.preventDefault(); setStatus('dragging'); }} onDrop={(e) => { e.preventDefault(); upload(e.dataTransfer.files[0]); }} 
         className={`border-2 border-dashed rounded-xl p-8 text-center ${status === 'dragging' ? 'border-accent bg-accent/5' : 'border-border'}`}>
      {status === 'idle' && <><Upload className="mx-auto text-text-muted mb-2" /><p>Drag resume here</p></>}
      {status === 'uploading' && <div className="h-1 bg-accent animate-pulse rounded-full" />}
      {status === 'done' && <><CheckCircle className="mx-auto text-green-400" /><p>Upload complete</p></>}
      {status === 'error' && <><AlertCircle className="mx-auto text-status-failed" /><p>Upload failed</p></>}
    </div>
  );
};
