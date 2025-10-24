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

interface SightingFilters {
  license_plate?: string;
  camera_id?: number | string;
  start_date?: string;
  end_date?: string;
}

interface SightingState {
  sightings: Sighting[]
  isLoading: boolean
  filters: SightingFilters
  totalSightings: number
  currentPage: number
  itemsPerPage: number
  setFilters: (filters: SightingFilters) => void
  setCurrentPage: (page: number) => void
  fetchSightings: () => Promise<void>
}

export const useSightingStore = create<SightingState>((set, get) => ({
  sightings: [],
  isLoading: false,
  filters: { license_plate: '', camera_id: '', start_date: '', end_date: '' },
  totalSightings: 0,
  currentPage: 1,
  itemsPerPage: 12,

  setFilters: (newFilters) => {
    set({ filters: { ...get().filters, ...newFilters }, currentPage: 1 }); // Reseta para a página 1 ao aplicar filtros
  },

  setCurrentPage: (page: number) => {
    set({ currentPage: page });
  },

  fetchSightings: async () => {
    set({ isLoading: true });
    const { filters, currentPage, itemsPerPage } = get();
    const params = {
      ...filters,
      skip: (currentPage - 1) * itemsPerPage,
      limit: itemsPerPage,
    };
    try {
      const { items, total } = await sightingService.getSightings(params);
      set({ sightings: items, totalSightings: total, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      toast.error('Erro ao carregar as detecções.');
    }
  },
}))