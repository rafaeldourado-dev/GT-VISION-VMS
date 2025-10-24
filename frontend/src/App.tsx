import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard'; 
import Settings from './pages/Settings';
import LandingPage from './pages/LandingPage';
import Analytics from './pages/Analytics';
import CamerasPage from './pages/CamerasPage'; // Importa a página de Câmeras
import DetectionsPage from './pages/DetectionsPage'; // Importe a nova página
import MapPage from './pages/MapPage'; // Importa a página do Mapa
import UserManagementPage from './pages/UserManagementPage'; // Importa a página de Usuários
import ProtectedRoute from './components/ProtectedRoute'; // CORREÇÃO: Importação adicionada
import NotificationProvider from './components/NotificationProvider';

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
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<Login />} />
            
            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            {/* ROTAS NOVAS ADICIONADAS AQUI */}
            <Route path="/cameras" element={<ProtectedRoute><CamerasPage /></ProtectedRoute>} />
            <Route path="/map" element={<ProtectedRoute><MapPage /></ProtectedRoute>} />
            <Route path="/detections" element={<ProtectedRoute><DetectionsPage /></ProtectedRoute>} />
            <Route path="/users" element={<ProtectedRoute><UserManagementPage /></ProtectedRoute>} />
            <Route path="/analytics" element={<ProtectedRoute><Analytics /></ProtectedRoute>} />
            <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
            
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </NotificationProvider>
      </Router>
    </>
  );
}

export default App;