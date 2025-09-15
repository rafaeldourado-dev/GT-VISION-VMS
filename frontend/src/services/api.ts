import axios from 'axios'
import toast from 'react-hot-toast'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1', 
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptors (código existente)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('vms_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('vms_token')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
        toast.error('Sessão expirada. Faça login novamente.')
      }
    }
    return Promise.reject(error)
  }
)

interface NewCameraData {
  name: string
  rtsp_url: string
  latitude?: number | null
  longitude?: number | null
}

export const authService = {
  login: async (email: string, password: string) => {
    const params = new URLSearchParams()
    params.append('username', email)
    params.append('password', password)
    const response = await api.post('/auth/token', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    return response.data
  },
  getMe: async () => {
    const response = await api.get('/auth/users/me')
    return response.data
  },
}

export const cameraService = {
  getCameras: async () => {
    const response = await api.get('/cameras/')
    return response.data
  },
  createCamera: async (cameraData: NewCameraData) => {
    const response = await api.post('/cameras', cameraData)
    return response.data
  },
  deleteCamera: async (cameraId: number) => {
    const response = await api.delete(`/cameras/${cameraId}`)
    return response.data
  },
}

// NOVO: Define o tipo para os filtros
interface SightingFilters {
  license_plate?: string;
}

export const sightingService = {
  // ATUALIZADO: Função agora aceita filtros
  getSightings: async (filters: SightingFilters = {}) => {
    const response = await api.get('/sightings/', { params: filters })
    return response.data
  },
}

export default api