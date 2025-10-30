// Conteúdo CORRIGIDO para GT-VISION-VMS/frontend/src/services/api.ts
import axios from 'axios';
import toast from 'react-hot-toast';
import { useAuthStore } from '../stores/authStore';

const api = axios.create({
  // --- CORREÇÃO 1 ---
  // Alterado 'http://127.0.0.1:8000/api/v1' para um caminho relativo.
  // Agora o navegador enviará a requisição para o Nginx (localhost:5173),
  // que irá repassar para o backend.
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  // --- FIM DA CORREÇÃO 1 ---
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
        
        useAuthStore.getState().setToken(access_token);
        
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        toast.error("Sua sessão expirou. Por favor, faça login novamente.");
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

interface CameraUpdateData {
  name?: string
  rtsp_url?: string
  latitude?: number | null
  longitude?: number | null
  is_active?: boolean
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
  forcePasswordChangeInitial: async (
    email: string,
    oldPassword: string,
    newPassword: string
  ) => {
    const response = await api.post('/auth/force-password-change-initial', {
      email,
      old_password: oldPassword,
      new_password: newPassword,
    });
    return response.data;
  },
  getMe: async (token: string) => {
    const response = await api.get('/auth/users/me', {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },
  refreshToken: async () => {
    const response = await api.post('/auth/refresh-token');
    return response.data;
  },
  updateOwnPassword: async (currentPassword: string, newPassword: string) => {
    const response = await api.put('/users/me/password', { current_password: currentPassword, new_password: newPassword });
    return response.data;
  },
};

export const cameraService = {
  getCameras: async () => {
    const response = await api.get('/cameras/');
    return response.data;
  },
  createCamera: async (cameraData: NewCameraData) => {
    // --- CORREÇÃO 2 ---
    // Adicionada a barra "/" no final para evitar o redirecionamento 307.
    const response = await api.post('/cameras/', cameraData);
    // --- FIM DA CORREÇÃO 2 ---
    return response.data;
  },
  updateCamera: async (cameraId: number, cameraData: CameraUpdateData) => {
    const response = await api.put(`/cameras/${cameraId}`, cameraData);
    return response.data;
  },
  deleteCamera: async (cameraId: number) => {
    const response = await api.delete(`/cameras/${cameraId}`);
    return response.data;
  },
  refreshThumbnail: async (cameraId: number) => { 
    const response = await api.post(`/cameras/${cameraId}/refresh_thumbnail`);
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
  resetPassword: async (userId: number, newPassword: string) => {
    const response = await api.post(`/users/${userId}/reset-password`, { new_password: newPassword });
    return response.data;
  },
};

interface SightingFilters {
  license_plate?: string;
  [key: string]: any; 
}

export const sightingService = {
  getSightings: async (filters: SightingFilters = {}) => {
    const response = await api.get('/sightings', { params: filters });
    return response.data;
  },
};

export const auditLogService = {
  getLogs: async (params: any) => {
    const response = await api.get('/audit-logs', { params });
    return response.data;
  },
};

export const dashboardService = {
  getStats: async () => {
    const response = await api.get('/dashboard/stats');
    return response.data;
  },
  getActiveCameras: async () => {
    const response = await api.get('/cameras/');
    return response.data;
  },
};

export default api;