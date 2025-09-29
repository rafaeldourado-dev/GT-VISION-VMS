import { create } from 'zustand'
import { authService } from '../services/api'
import toast from 'react-hot-toast'

interface User {
  id: number
  email: string
  is_active: boolean
  full_name: string
  client_id: number
  role: string
}

// ATUALIZADO: Adicionamos 'setToken' e 'isAuthChecked' à interface
interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  isAuthChecked: boolean
  setToken: (token: string) => void
  login: (email: string, password: string) => Promise<boolean>
  logout: () => void
  checkAuth: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  isAuthChecked: false,

  // NOVA FUNÇÃO: Implementação do setToken
  setToken: (token: string) => {
    set({ token, isAuthenticated: !!token });
  },

  login: async (email: string, password: string) => {
    set({ isLoading: true });
    try {
      const response = await authService.login(email, password);
      const { access_token } = response;
      
      // CORREÇÃO: Passamos o 'access_token' para a função getMe
      const userData = await authService.getMe(access_token);

      // CORREÇÃO CRÍTICA: Adicionar isAuthChecked: true
      set({
        user: userData,
        token: access_token,
        isAuthenticated: true,
        isLoading: false,
        isAuthChecked: true, // <--- CORREÇÃO APLICADA AQUI
      });

      toast.success('Login realizado com sucesso!');
      return true;
    } catch (error: any) {
      // CORREÇÃO CRÍTICA: Adicionar isAuthChecked: true
      set({ 
        isLoading: false, 
        token: null, 
        isAuthenticated: false,
        isAuthChecked: true, // <--- CORREÇÃO APLICADA AQUI
      });
      if (error.response?.status === 401 || error.response?.status === 400) {
        toast.error('Email ou senha incorretos.');
      } else {
        toast.error('Erro ao fazer login. Tente novamente.');
      }
      return false;
    }
  },

  logout: () => {
    // CORREÇÃO CRÍTICA: Adicionar isAuthChecked: true
    set({ 
        user: null, 
        token: null, 
        isAuthenticated: false,
        isAuthChecked: true, // <--- CORREÇÃO APLICADA AQUI
    });
    window.location.href = '/login';
    toast.success('Logout realizado com sucesso!');
  },

  checkAuth: async () => {
    try {
      const response = await authService.refreshToken();
      const { access_token } = response;
      
      // CORREÇÃO: Passamos o 'access_token' para a função getMe
      const userData = await authService.getMe(access_token);
      
      set({
        user: userData,
        token: access_token,
        isAuthenticated: true,
        isAuthChecked: true,
      });
    } catch (error) {
      set({
        user: null,
        token: null,
        isAuthenticated: false,
        isAuthChecked: true,
      });
    }
  },
}));