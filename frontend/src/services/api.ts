import axios from 'axios';
import toast from 'react-hot-toast';
import { useAuthStore } from '../stores/authStore';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, 
});

api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const response = await api.post('/auth/refresh-token'); 
        const { access_token } = response.data;
        
        // CORREÇÃO: Esta chamada agora funciona porque 'setToken' existe no authStore
        useAuthStore.getState().setToken(access_token);
        
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        useAuthStore.getState().logout();
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

interface NewCameraData {
  name: string
  rtsp_url: string
  latitude?: number | null
  longitude?: number | null
}

export const authService = {
  login: async (email: string, password: string) => {
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);
    const response = await api.post('/auth/token', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },
  // CORREÇÃO: A função agora aceita um argumento 'token'
  getMe: async (token: string) => {
    const response = await api.get('/auth/users/me', {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },
  refreshToken: async () => {
    const response = await api.post('/auth/refresh-token');
    return response.data;
  }
};

export const cameraService = {
  getCameras: async () => {
    const response = await api.get('/cameras/');
    return response.data;
  },
  createCamera: async (cameraData: NewCameraData) => {
    const response = await api.post('/cameras', cameraData);
    return response.data;
  },
  deleteCamera: async (cameraId: number) => {
    const response = await api.delete(`/cameras/${cameraId}`);
    return response.data;
  },
};

export const userService = {
  getUsers: async () => {
    const response = await api.get('/users/');
    return response.data;
  },
  createUser: async (userData: any) => {
    const response = await api.post('/users/', userData);
    return response.data;
  },
  updateUser: async (userId: number, userData: any) => {
    const response = await api.put(`/users/${userId}`, userData);
    return response.data;
  },
  deleteUser: async (userId: number) => {
    const response = await api.delete(`/users/${userId}`);
    return response.data;
  },
};

interface SightingFilters {
  license_plate?: string;
  [key: string]: any; // Permite outras propriedades de filtro
}

export const sightingService = {
  getSightings: async (filters: SightingFilters = {}) => {
    const response = await api.get('/sightings', { params: filters });
    return response.data;
  },
};

export default api;