import api from './client';
import type { UserProfile, ProfileUpdateResponse } from '../interfaces/profile';

export const profileService = {
    getProfile: () =>
        api.get<UserProfile>('/profile/me'),

    updateProfile: (data: Partial<UserProfile>) =>
        api.put<ProfileUpdateResponse>('/profile/me', data),

    uploadResume: (file: File) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post<{ url: string }>('/profile/resume', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
    }
};