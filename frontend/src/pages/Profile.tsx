import { useState } from 'react';
import { useProfile } from '../hooks/useProfile';
import { Button } from '../components/ui/Button';
import { ResumeUpload } from '../components/profile/ResumeUpload';
import api from '../api';

export default function Profile() {
  const { profile, loading } = useProfile();
  const [name, setName] = useState(profile?.name || '');
  if (loading) return <div>Loading...</div>;
  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="bg-surface border border-border rounded-xl p-5">
        <h2 className="text-sm font-semibold mb-4 uppercase text-text-muted">Account Information</h2>
        <input className="w-full bg-elevated border border-border rounded-lg px-3 py-2 mb-4" value={name} onChange={e => setName(e.target.value)} />
        <Button onClick={() => api.put('/profile/me', { name })}>Save</Button>
      </div>
      <div className="bg-surface border border-border rounded-xl p-5">
        <h2 className="text-sm font-semibold mb-4 uppercase text-text-muted">Resume</h2>
        {profile?.resume_filename && <p className="mb-2 text-sm text-text-primary font-mono">{profile.resume_filename}</p>}
        <ResumeUpload onSuccess={() => window.location.reload()} />
      </div>
    </div>
  );
}
