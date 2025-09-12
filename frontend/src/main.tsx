import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import 'leaflet/dist/leaflet.css' // GARANTA QUE ESTA LINHA ESTÁ AQUI E ANTES DO INDEX.CSS
import './index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)