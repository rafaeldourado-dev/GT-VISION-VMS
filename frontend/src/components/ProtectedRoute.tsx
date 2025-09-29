// src/components/ProtectedRoute.tsx (CORRIGIDO)

import React, { useEffect } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

interface ProtectedRouteProps {
  children: React.ReactNode
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  // ATUALIZAÇÃO: Incluir isAuthChecked da store para controlar o estado de carregamento
  const { isAuthenticated, isAuthChecked, checkAuth } = useAuthStore()

  useEffect(() => {
    // Garante que a checagem de autenticação rode se ainda não tiver ocorrido
    if (!isAuthChecked) {
        checkAuth()
    }
  }, [checkAuth, isAuthChecked])

  // 1. NOVO: Mostrar um estado de carregamento enquanto isAuthChecked é falso.
  // Isso impede que o React faça o redirecionamento imediato antes de saber se há sessão.
  if (!isAuthChecked) {
    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="ml-3 text-gray-600">A validar sessão...</p>
        </div>
    )
  }

  // 2. Se a checagem terminou (isAuthChecked é true) e não está autenticado, redireciona
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // 3. Se a checagem terminou e está autenticado, mostra o conteúdo (Dashboard)
  return <>{children}</>
}

export default ProtectedRoute