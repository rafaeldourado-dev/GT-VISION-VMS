import { create } from 'zustand'
import { cameraService } from '../services/api'
import toast from 'react-hot-toast'

interface Camera {
  id: number
  name: string
  rtsp_url: string
  latitude?: number | null
  longitude?: number | null
  is_active: boolean
  client_id: number
}

interface NewCameraData {
  name: string
  rtsp_url: string
  latitude?: number | null
  longitude?: number | null
}

interface CameraState {
  cameras: Camera[]
  isLoading: boolean
  fetchCameras: () => Promise<void>
  addCamera: (cameraData: NewCameraData) => Promise<boolean>
  deleteCamera: (cameraId: number) => Promise<void>
}

export const useCameraStore = create<CameraState>((set) => ({
  cameras: [],
  isLoading: false,

  fetchCameras: async () => {
    set({ isLoading: true })
    try {
      const cameras = await cameraService.getCameras()
      set({ cameras, isLoading: false })
    } catch (error) {
      set({ isLoading: false })
      toast.error('Erro ao carregar câmaras.')
    }
  },

  addCamera: async (cameraData: NewCameraData) => {
    try {
      const newCamera = await cameraService.createCamera(cameraData)
      set(state => ({
        cameras: [...state.cameras, newCamera]
      }))
      toast.success('Câmara adicionada com sucesso!')
      return true
    } catch (error: any) {
      if (error.response?.status === 409) {
        toast.error('URL RTSP já existe.')
      } else {
        toast.error('Erro ao adicionar câmara.')
      }
      return false
    }
  },

  deleteCamera: async (cameraId: number) => {
    try {
      await cameraService.deleteCamera(cameraId)
      set(state => ({
        cameras: state.cameras.filter(camera => camera.id !== cameraId)
      }))
      toast.success('Câmara excluída com sucesso!')
    } catch (error) {
      toast.error('Erro ao excluir câmara.')
    }
  },
}))