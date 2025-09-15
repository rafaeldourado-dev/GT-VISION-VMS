import { create } from 'zustand'
import { sightingService } from '../services/api'
import toast from 'react-hot-toast'

interface Sighting {
  id: number
  license_plate: string
  vehicle_color: string | null
  vehicle_model: string | null
  image_path: string | null
  timestamp: string
  camera: {
    name: string
  }
}

// NOVO: Define a estrutura dos filtros
interface SightingFilters {
  license_plate?: string;
}

interface SightingState {
  sightings: Sighting[]
  isLoading: boolean
  filters: SightingFilters // Adiciona os filtros ao estado
  setFilters: (filters: SightingFilters) => void // Adiciona uma função para atualizar os filtros
  fetchSightings: () => Promise<void>
}

export const useSightingStore = create<SightingState>((set, get) => ({
  sightings: [],
  isLoading: false,
  filters: {}, // Estado inicial dos filtros

  setFilters: (newFilters) => {
    set({ filters: { ...get().filters, ...newFilters } })
  },

  fetchSightings: async () => {
    set({ isLoading: true })
    try {
      const sightingsData = await sightingService.getSightings(get().filters)
      set({ sightings: sightingsData, isLoading: false })
    } catch (error) {
      set({ isLoading: false })
      toast.error('Erro ao carregar as detecções.')
    }
  },
}))