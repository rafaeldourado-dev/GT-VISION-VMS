import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';

// Imports agora usando o alias '@'
import Login from '@/pages/Login';
import Dashboard from '@/pages/Dashboard';
import Settings from '@/pages/Settings';
// import LandingPage from '@/pages/LandingPage'; // Removido - Não será mais usado
import Analytics from '@/pages/Analytics';
import CamerasPage from '@/pages/CamerasPage';
import DetectionsPage from '@/pages/DetectionsPage';
// import MapPage from '@/pages/MapPage'; // Removido - Corrigindo o erro de build
import UserManagementPage from '@/pages/UserManagementPage';
import ProtectedRoute from '@/components/ProtectedRoute';
import NotificationProvider from '@/components/NotificationProvider';

// Importa a página de mudança forçada de senha
import ForcePasswordChangePage from '@/pages/ForcePasswordChangePage';

function App() {
  return (
    <>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 5000,
          style: { background: '#363636', color: '#fff' },
          success: { style: { background: '#10b981' } },
          error: { style: { background: '#ef4444' } },
        }}
      />
      <Router>
        <NotificationProvider>
          <Routes>
            {/* CORREÇÃO DA PÁGINA EM BRANCO:
              A rota "/" agora redireciona para "/dashboard", que é a página principal.
              O ProtectedRoute irá então redirecionar para /login se o usuário não estiver logado.
            */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            
            <Route path="/login" element={<Login />} />
            
            {/* Rota para mudança de senha forçada */}
            <Route
              path="/force-password-change"
              element={<ForcePasswordChangePage />}
            />

            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/cameras"
              element={
                <ProtectedRoute>
                  <CamerasPage />
                </ProtectedRoute>
              }
            />
            
            {/* Rota do Mapa Removida - Corrigindo o erro de build */}
            
            <Route
              path="/detections"
              element={
                <ProtectedRoute>
                  <DetectionsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/users"
              element={
                <ProtectedRoute>
                  <UserManagementPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/analytics"
              element={
                <ProtectedRoute>
                  <Analytics />
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <Settings />
                </ProtectedRoute>
              }
            />

            {/* O "catch-all" (404) agora também redireciona para o dashboard */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </NotificationProvider>
      </Router>
    </>
  );
}

export default App;