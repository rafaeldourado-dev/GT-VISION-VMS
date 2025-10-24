import React, { useEffect, useState } from 'react';
import { Plus, Camera, Eye, CheckCircle } from 'lucide-react';
import { useCameraStore } from '../stores/cameraStore';
import AddCameraModal from '../components/AddCameraModal';
import VideoStreamModal from '../components/VideoStreamModal';
import AppLayout from '../components/AppLayout';
import CameraList from '../components/CameraList'; // Importa o novo componente

const StatCard: React.FC<{ title: string; value: string | number; icon: React.ReactNode }> = ({ title, value, icon }) => (
  <div className="bg-white p-6 rounded-lg shadow-sm flex items-center">
    {icon}
    <div className="ml-4">
      <p className="text-sm font-medium text-gray-600">{title}</p>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  </div>
);

const Dashboard: React.FC = () => {
  const { cameras, isLoading, fetchCameras } = useCameraStore();
  const [viewingCamera, setViewingCamera] = useState<{id: number, name: string} | null>(null);

  useEffect(() => {
    fetchCameras();
  }, [fetchCameras]);

  return (
    <AppLayout>
      <h2 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h2>
      <p className="text-gray-600 mb-8">Visão geral do seu sistema de monitoramento.</p>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <StatCard title="Total de Câmaras" value={cameras.length} icon={<Camera className="w-8 h-8 text-blue-600" />} />
        {/* Este card pode ser alterado para mostrar câmaras ativas vs inativas */}
        <StatCard title="Câmaras Ativas" value={cameras.filter(c => c.is_active).length} icon={<Eye className="w-8 h-8 text-green-600" />} />
        <StatCard title="Status do Sistema" value="Online" icon={<CheckCircle className="w-8 h-8 text-green-600" />} />
      </div>

      {isLoading ? (
          <div className="p-8 text-center bg-white rounded-lg"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div><p className="mt-2 text-gray-600">A carregar câmaras...</p></div>
      ) : cameras.length === 0 ? (
          <div className="p-8 text-center bg-white rounded-lg shadow-sm"><Camera className="w-12 h-12 text-gray-400 mx-auto mb-4" /><h3 className="text-lg font-medium text-gray-900 mb-2">Nenhuma câmara registada</h3><p className="text-gray-600">Vá para a página de 'Câmeras' para adicionar a sua primeira.</p></div>
      ) : (
        <CameraList onViewCamera={setViewingCamera} />
      )}
      <VideoStreamModal camera={viewingCamera} onClose={() => setViewingCamera(null)} />
    </AppLayout>
  );
};

export default Dashboard;