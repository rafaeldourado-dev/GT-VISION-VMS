import { create } from 'zustand';
import { authService } from '../services/api';
import toast from 'react-hot-toast';

interface User {
  id: number;
  email: string;
  is_active: boolean;
  full_name: string;
  password_change_required: boolean;
  client_id: number;
  role: string;
}

// --- ALTERAÇÃO AQUI ---
// O tipo de retorno do 'login' está correto.
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isAuthChecked: boolean;
  setToken: (token: string) => void;
  login: (
    email: string,
    password: string
  ) => Promise<'SUCCESS' | 'PASSWORD_CHANGE_REQUIRED' | 'FAILED'>; // Alterado
  logout: () => void;
  updateOwnPassword: (
    currentPassword: string,
    newPassword: string
  ) => Promise<boolean>;
  checkAuth: () => Promise<void>;
}
// -----------------------

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  isAuthChecked: false,

  setToken: (token: string) => {
    set({ token, isAuthenticated: !!token });
  },

  login: async (email: string, password: string) => {
    set({ isLoading: true });
    try {
      // 1. Attempt to log in. If it fails with 403, the catch block will handle it.
      const response = await authService.login(email, password);
      const { access_token } = response;

      // 2. If login is successful, fetch user data.
      const userData = await authService.getMe(access_token);

      // 3. Store user data and token in the state.
      set({
        user: userData,
        token: access_token,
        isAuthenticated: true,
        isLoading: false,
        isAuthChecked: true,
      });
      
      toast.success('Login realizado com sucesso!');
      return 'SUCCESS';

    } catch (error: any) {
      set({
        isLoading: false,
        token: null,
        isAuthenticated: false,
        isAuthChecked: true,
      });
      
      // 4. Check if the error is the specific 403 for required password change.
      if (
        error.response?.status === 403 &&
        error.response?.headers['x-password-change-required'] === 'true'
      ) {
        toast.error('Você precisa alterar sua senha antes de continuar.');
        // Return the signal for the Login component to redirect.
        return 'PASSWORD_CHANGE_REQUIRED';
      }
      
      // 5. Handle other errors like incorrect credentials.
      if (error.response?.status === 401 || error.response?.status === 400) {
        toast.error('Email ou senha incorretos.');
      } else {
        toast.error('Erro ao fazer login. Tente novamente.');
        console.error('Login error:', error);
      }
      // Retornamos falha
      return 'FAILED';
    }
  },

  updateOwnPassword: async (currentPassword, newPassword) => {
    try {
      await authService.updateOwnPassword(currentPassword, newPassword);
      // Após a troca, buscamos os dados do usuário novamente para limpar a flag
      const token = useAuthStore.getState().token;
      if (token) {
        const userData = await authService.getMe(token);
        set({ user: userData });
      }
      return true;
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao alterar a senha.');
      return false;
    }
  },

  logout: () => {
    set({ user: null, token: null, isAuthenticated: false, isAuthChecked: true });
    window.location.href = '/login';
    toast.success('Logout realizado com sucesso!');
  },

  checkAuth: async () => {
    try {
      const response = await authService.refreshToken();
      const { access_token } = response;

      const userData = await authService.getMe(access_token);

      set({
        user: userData,
        token: access_token,
        isAuthenticated: true,
        isAuthChecked: true,
      });

      // --- ADIÇÃO IMPORTANTE ---
      // Se o usuário recarregar a página e ainda precisar trocar a senha,
      // nós o forçamos a ir para a página de troca.
      if (userData.password_change_required) {
        // Evita loop se já estivermos na página
        if (window.location.pathname !== '/force-password-change') {
          window.location.href = '/force-password-change';
        }
      }
      // -------------------------
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
