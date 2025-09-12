// NOVO ARQUIVO: frontend/src/pages/MapPage.tsx
import React, { useState, useEffect } from 'react';
import AppLayout from '../components/AppLayout';
import MapDisplay from '../components/MapDisplay';
import VideoStreamModal from '../components/VideoStreamModal';
import { useCameraStore } from '../stores/cameraStore';
import { Map } from 'lucide-react';

const MapPage: React.FC = () => {
  const [viewingCamera, setViewingCamera] = useState<{id: number, name: string} | null>(null);
  const { fetchCameras } = useCameraStore();

  // Garante que as câmeras (com suas coordenadas) sejam carregadas ao entrar na página
  useEffect(() => {
    fetchCameras();
  }, [fetchCameras]);

  return (
    <AppLayout>
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 flex items-center">
            <Map className="w-7 h-7 mr-3" />
            Visualização no Mapa
        </h2>
        <p className="text-gray-600 mt-1">Localize e visualize suas câmeras geograficamente.</p>
      </div>

      <MapDisplay onViewCamera={setViewingCamera} />

      <VideoStreamModal camera={viewingCamera} onClose={() => setViewingCamera(null)} />
    </AppLayout>
  );
};

export default MapPage;