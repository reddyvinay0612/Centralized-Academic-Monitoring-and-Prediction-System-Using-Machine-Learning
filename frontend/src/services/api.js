import axios from 'axios';

// Base API URL configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Enables cookies for refresh token rotation
});

// Request Interceptor: Attach JWT Token from in-memory session or localStorage
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('camps_access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Global 401 handling & token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Attempt refresh
        const refreshResponse = await axios.post(
          `${API_BASE_URL}/auth/refresh`,
          {},
          { withCredentials: true }
        );

        if (refreshResponse.data?.access_token) {
          const newToken = refreshResponse.data.access_token;
          localStorage.setItem('camps_access_token', newToken);
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Clear session on refresh failure
        localStorage.removeItem('camps_access_token');
        localStorage.removeItem('camps_user');
      }
    }

    return Promise.reject(error);
  }
);

export default api;
