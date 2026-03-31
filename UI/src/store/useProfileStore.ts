import { create } from 'zustand';
import type { UserProfile } from '../interfaces/profile';
import { profileService } from '../api/profileService';

interface ProfileState {
    profile: UserProfile | null;
    isLoading: boolean;
    fetchProfile: () => Promise<void>;
    setProfile: (profile: UserProfile) => void;
}

export const useProfileStore = create<ProfileState>((set) => ({
    profile: null,
    isLoading: false,
    fetchProfile: async () => {
        set({ isLoading: true });
        try {
            const response = await profileService.getProfile();
            set({ profile: response.data, isLoading: false });
        } catch (error) {
            set({ isLoading: false });
            console.error("Failed to fetch profile", error);
        }
    },
    setProfile: (profile) => set({ profile }),
}));