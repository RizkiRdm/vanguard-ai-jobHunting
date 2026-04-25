export default axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000', withCredentials: true });
