export interface UserProfile {
    id?: string;
    full_name: string;
    email: string;
    phone: string;
    target_role: string;
    expected_salary: string;
    summary: string;
    resume_url?: string;
    skills: string[];
    experience_years: number;
    location: string;
}

export interface ProfileUpdateResponse {
    status: string;
    message: string;
    data?: UserProfile;
}