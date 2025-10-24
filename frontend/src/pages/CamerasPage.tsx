import React, { useEffect, useState } from 'react';
import AppLayout from '../components/AppLayout';
import { useCameraStore } from '../stores/cameraStore';
import { Camera, PlusCircle, Video, VideoOff, MoreVertical, Edit, Trash2 } from 'lucide-react';
import AddCameraModal from '../components/AddCameraModal'; // Importa o modal

const CamerasPage: React.FC = () => {
  const { cameras, isLoading, fetchCameras, deleteCamera } = useCameraStore();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [cameraToEdit, setCameraToEdit] = useState<any | null>(null);

  useEffect(() => {
    fetchCameras();
  }, [fetchCameras]);

  const handleAddCamera = () => {
    setCameraToEdit(null);
    setIsModalOpen(true);
  };

  const handleEditCamera = (camera: any) => {
    setCameraToEdit(camera);
    setIsModalOpen(true);
  }

  return (
    <AppLayout>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 flex items-center">
            <Camera className="w-7 h-7 mr-3" />
            Gerenciamento de Câmeras
          </h2>
          <p className="text-gray-600 mt-1">Adicione, edite e visualize suas câmeras de monitoramento.</p>
        </div>
        <button
          onClick={handleAddCamera}
          className="flex items-center justify-center bg-blue-600 text-white px-4 py-2 rounded-lg shadow-sm hover:bg-blue-700 transition-colors"
        >
          <PlusCircle className="w-5 h-5 mr-2" />
          Adicionar Câmera
        </button>
      </div>

      {isLoading ? (
        <div className="p-8 text-center bg-white rounded-lg shadow-sm">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Carregando câmeras...</p>
        </div>
      ) : cameras.length === 0 ? (
        <div className="p-8 text-center bg-white rounded-lg shadow-sm">
          <Camera className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Nenhuma câmera cadastrada</h3>
          <p className="text-gray-600">Clique em "Adicionar Câmera" para começar.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {cameras.map((camera) => (
            <div key={camera.id} className="bg-white rounded-lg shadow-sm p-4 flex flex-col">
              <div className="flex justify-between items-start">
                <h3 className="font-bold text-gray-800 mb-1">{camera.name}</h3>
                {/* Menu de Ações (a ser implementado com dropdown) */}
                <div className="relative">
                   <button onClick={() => deleteCamera(camera.id)} className="text-gray-400 hover:text-red-600 p-1 rounded-full">
                      <Trash2 className="w-4 h-4" />
                   </button>
                </div>
              </div>
              <p className="text-sm text-gray-500 truncate" title={camera.rtsp_url}>
                {camera.rtsp_url}
              </p>
              <div className="flex-grow"></div>
              <div className="mt-4 flex justify-between items-center">
                <div className={`flex items-center text-sm ${camera.is_active ? 'text-green-600' : 'text-red-600'}`}>
                  {camera.is_active ? <Video className="w-4 h-4 mr-1" /> : <VideoOff className="w-4 h-4 mr-1" />}
                  {camera.is_active ? 'Ativa' : 'Inativa'}
                </div>
                {/* Botão de edição (a ser implementado) */}
                <button onClick={() => handleEditCamera(camera)} className="text-gray-400 hover:text-blue-600 p-1 rounded-full">
                  <Edit className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
      <AddCameraModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} cameraToEdit={cameraToEdit} />
    </AppLayout>
  );
};

export default CamerasPage;