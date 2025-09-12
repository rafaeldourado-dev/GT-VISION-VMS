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

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<boolean>
  logout: () => void
  checkAuth: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('vms_token'),
  isAuthenticated: !!localStorage.getItem('vms_token'),
  isLoading: false,

  login: async (email: string, password: string) => {
    set({ isLoading: true })
    try {
      const response = await authService.login(email, password)
      const { access_token } = response

      localStorage.setItem('vms_token', access_token)
      
      // Define o token no estado antes de chamar getMe
      set({ token: access_token })

      const userData = await authService.getMe()

      set({
        user: userData,
        isAuthenticated: true,
        isLoading: false,
      })

      toast.success('Login realizado com sucesso!')
      return true
    } catch (error: any) {
      set({ isLoading: false })
      if (error.response?.status === 401 || error.response?.status === 400) {
        toast.error('Email ou senha incorretos.')
      } else {
        toast.error('Erro ao fazer login. Tente novamente.')
      }
      return false
    }
  },

  logout: () => {
    localStorage.removeItem('vms_token')
    set({
      user: null,
      token: null,
      isAuthenticated: false,
    })
    // Redireciona para a página de login para uma experiência mais fluida
    window.location.href = '/login'
    toast.success('Logout realizado com sucesso!')
  },

  checkAuth: async () => {
    const token = localStorage.getItem('vms_token')
    if (!token) {
      set({ isAuthenticated: false, user: null, token: null })
      return
    }

    try {
      const userData = await authService.getMe()
      set({
        user: userData,
        token,
        isAuthenticated: true,
      })
    } catch (error) {
      // Se o token for inválido, limpa tudo
      localStorage.removeItem('vms_token')
      set({
        user: null,
        token: null,
        isAuthenticated: false,
      })
    }
  },
}))