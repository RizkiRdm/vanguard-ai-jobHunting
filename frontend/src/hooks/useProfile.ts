import { useState, useEffect } from 'react';
import { UserProfile } from '../types';
import api from '../api';

export const useProfile = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    api.get('/profile/me')
      .then(res => setProfile(res.data))
      .catch(() => setError('Failed to load profile'))
      .finally(() => setLoading(false));
  }, []);
  return { profile, loading, error };
};
