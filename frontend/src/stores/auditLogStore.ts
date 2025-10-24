import { create } from 'zustand';
import { auditLogService } from '../services/api';
import toast from 'react-hot-toast';

interface Actor {
  id: number;
  email: string;
  full_name: string;
}

interface AuditLog {
  id: number;
  timestamp: string;
  action: string;
  actor: Actor;
  target_id: number | null;
  target_type: string | null;
  details: string | null;
}

interface AuditLogFilters {
  actor_id?: number | null;
  action?: string | null;
  date_range?: [Date | null, Date | null];
}

interface AuditLogState {
  logs: AuditLog[];
  isLoading: boolean;
  totalLogs: number;
  currentPage: number;
  itemsPerPage: number;
  filters: AuditLogFilters;
  setFilters: (newFilters: Partial<AuditLogFilters>) => void;
  setCurrentPage: (page: number) => void;
  fetchLogs: () => Promise<void>;
}

export const useAuditLogStore = create<AuditLogState>((set, get) => ({
  logs: [],
  isLoading: false,
  totalLogs: 0,
  currentPage: 1,
  itemsPerPage: 15,
  filters: {},

  setFilters: (newFilters) => {
    set((state) => ({
      filters: { ...state.filters, ...newFilters },
      currentPage: 1, // Reseta para a primeira página ao aplicar filtros
    }));
  },

  setCurrentPage: (page: number) => {
    set({ currentPage: page });
  },

  fetchLogs: async () => {
    set({ isLoading: true });
    const { currentPage, itemsPerPage, filters } = get();
    const params: any = {
      skip: (currentPage - 1) * itemsPerPage,
      limit: itemsPerPage,
    };

    if (filters.actor_id) params.actor_id = filters.actor_id;
    if (filters.action) params.action = filters.action;
    if (filters.date_range?.[0]) params.start_date = filters.date_range[0].toISOString();
    if (filters.date_range?.[1]) params.end_date = filters.date_range[1].toISOString();

    try {
      const { items, total } = await auditLogService.getLogs(params);
      set({ logs: items, totalLogs: total, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      toast.error('Erro ao carregar logs de auditoria.');
    }
  },
}));