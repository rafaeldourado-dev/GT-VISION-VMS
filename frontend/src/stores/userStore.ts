import { create } from 'zustand';
import { userService } from '../services/api';
import toast from 'react-hot-toast';

interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  role: string;
  client_id: number;
}

type UserCreateData = Omit<User, 'id' | 'client_id'>;
type UserUpdateData = Partial<Omit<User, 'id' | 'client_id'>>;

interface UserState {
  users: User[];
  isLoading: boolean;
  fetchUsers: () => Promise<void>;
  addUser: (userData: UserCreateData) => Promise<boolean>;
  updateUser: (userId: number, userData: UserUpdateData) => Promise<boolean>;
  deleteUser: (userId: number) => Promise<void>;
  resetPassword: (userId: number, newPassword: string) => Promise<boolean>;
}

export const useUserStore = create<UserState>((set) => ({
  users: [],
  isLoading: false,

  fetchUsers: async () => {
    set({ isLoading: true });
    try {
      const users = await userService.getUsers();
      set({ users, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      toast.error('Erro ao carregar usuários.');
    }
  },

  addUser: async (userData) => {
    try {
      const newUser = await userService.createUser(userData);
      set((state) => ({ users: [...state.users, newUser] }));
      toast.success('Usuário adicionado com sucesso!');
      return true;
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao adicionar usuário.');
      return false;
    }
  },

  updateUser: async (userId, userData) => {
    try {
      const updatedUser = await userService.updateUser(userId, userData);
      set((state) => ({
        users: state.users.map((user) =>
          user.id === userId ? updatedUser : user
        ),
      }));
      toast.success('Usuário atualizado com sucesso!');
      return true;
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao atualizar usuário.');
      return false;
    }
  },

  deleteUser: async (userId) => {
    try {
      await userService.deleteUser(userId);
      set((state) => ({ users: state.users.filter((user) => user.id !== userId) }));
      toast.success('Usuário excluído com sucesso!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao excluir usuário.');
    }
  },

  resetPassword: async (userId, newPassword) => {
    try {
      await userService.resetPassword(userId, newPassword);
      toast.success('Senha redefinida com sucesso!');
      return true;
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erro ao redefinir a senha.');
      return false;
    }
  },
}));