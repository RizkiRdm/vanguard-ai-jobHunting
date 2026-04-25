import axios from 'axios';
const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000', withCredentials: true });

api.interceptors.response.use(
  (res) => res,
  (error) => {
    const status = error.response?.status;
    if (status === 401) window.location.href = '/login';
    if (status === 429) console.error('Too many requests.');
    if (status === 500) console.error('Server error.');
    return Promise.reject(error);
  }
);
export default api;
