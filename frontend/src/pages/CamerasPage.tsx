import React, { useEffect, useState } from 'react';
import { VideoCameraIcon, ArrowPathIcon, EyeIcon, TrashIcon, PlusIcon } from '@heroicons/react/24/outline';
import { useCameraStore } from '../stores/cameraStore';
import { useAuthStore } from '../stores/authStore';
import AppLayout from '../components/AppLayout';
import AddCameraModal from '../components/AddCameraModal';
import StreamModal from '../components/StreamModal.tsx'; // Explicitamente adiciona a extensão .tsx
import { Camera } from '../types'; // Supondo que você tenha um arquivo de tipos

const CamerasPage: React.FC = () => {
  const { cameras, isLoading, fetchCameras, deleteCamera, refreshCameraThumbnail } = useCameraStore();
  const { token } = useAuthStore();
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isStreamModalOpen, setIsStreamModalOpen] = useState(false);
  const [selectedCamera, setSelectedCamera] = useState<Camera | null>(null);
  const [refreshing, setRefreshing] = useState<Record<number, boolean>>({});

  useEffect(() => {
    fetchCameras();
  }, [fetchCameras]);

  const handleRefreshThumbnail = async (cameraId: number) => {
    setRefreshing(prev => ({ ...prev, [cameraId]: true }));
    await refreshCameraThumbnail(cameraId);
    // O store já tem um timeout para refetch, então só precisamos esperar
    setTimeout(() => {
      setRefreshing(prev => ({ ...prev, [cameraId]: false }));
    }, 3500); // Um pouco mais que o timeout do store
  };

  const handleDelete = async (cameraId: number) => {
    if (window.confirm('Tem certeza que deseja excluir esta câmera? Esta ação não pode ser desfeita.')) {
      await deleteCamera(cameraId);
    }
  };

  const openStreamModal = (camera: Camera) => {
    setSelectedCamera(camera);
    setIsStreamModalOpen(true);
  };

  return (
    <AppLayout>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Câmeras</h2>
          <p className="text-gray-600">Gerencie suas câmeras e visualize os streams.</p>
        </div>
        <button
          onClick={() => setIsAddModalOpen(true)}
          className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors"
        >
          <PlusIcon className="w-5 h-5 mr-2" />
          Adicionar Câmera
        </button>
      </div>

      {isLoading ? (
        <div className="text-center p-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div><p className="mt-2">Carregando câmeras...</p></div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm">
          <ul role="list" className="divide-y divide-gray-200">
            {cameras.map((camera) => (
              <li key={camera.id} className="flex items-center justify-between p-4 hover:bg-gray-50">
                <div className="flex items-center gap-4">
                  {camera.thumbnail_url ? (
                    <img
                      src={camera.thumbnail_url}
                      alt={camera.name}
                      className="h-12 w-12 rounded-full object-cover bg-gray-200"
                      onError={(e) => { e.currentTarget.src = '/placeholder.png'; }} // Fallback
                    />
                  ) : (
                    <div className="h-12 w-12 rounded-full bg-gray-200 flex items-center justify-center">
                      <VideoCameraIcon className="h-6 w-6 text-gray-400" />
                    </div>
                  )}
                  <div className="flex-grow">
                    <p className="text-sm font-semibold text-gray-900">{camera.name}</p>
                    <p className="text-sm text-gray-500">{camera.rtsp_url}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleRefreshThumbnail(camera.id)}
                    disabled={refreshing[camera.id]}
                    className="p-2 text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Atualizar thumbnail"
                  >
                    {refreshing[camera.id] ? (
                      <ArrowPathIcon className="h-5 w-5 animate-spin" />
                    ) : (
                      <ArrowPathIcon className="h-5 w-5" />
                    )}
                  </button>
                  <button
                    onClick={() => openStreamModal(camera)}
                    className="p-2 text-blue-500 hover:text-blue-700"
                    title="Ver stream"
                  >
                    <EyeIcon className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => handleDelete(camera.id)}
                    className="p-2 text-red-500 hover:text-red-700"
                    title="Excluir câmera"
                  >
                    <TrashIcon className="h-5 w-5" />
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      <AddCameraModal isOpen={isAddModalOpen} onClose={() => setIsAddModalOpen(false)} />
      {selectedCamera && token && (
        <StreamModal
          isOpen={isStreamModalOpen}
          onClose={() => setIsStreamModalOpen(false)}
          camera={selectedCamera}
          token={token}
        />
      )}
    </AppLayout>
  );
};

export default CamerasPage;