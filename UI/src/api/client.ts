import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    withCredentials: true,
});

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 429) {
            alert("Rate limit exceeded. Please slow down.");
        }
        return Promise.reject(error);
    }
);

export default api;