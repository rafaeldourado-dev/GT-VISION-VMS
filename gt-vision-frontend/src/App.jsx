
import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import Layout from './components/Layout'
import DashboardPage from './pages/DashboardPage'
import CamerasPage from './pages/CamerasPage'
import SightingsPage from './pages/SightingsPage'
import TicketsPage from './pages/TicketsPage'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={
        <ProtectedRoute>
          <Layout />
        </ProtectedRoute>
      }>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="cameras" element={<CamerasPage />} />
        <Route path="sightings" element={<SightingsPage />} />
        <Route path="tickets" element={<TicketsPage />} />
      </Route>
    </Routes>
  )
}

export default App
