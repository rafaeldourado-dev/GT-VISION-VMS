import React from 'react';
import { useCameraStore } from '../stores/cameraStore'; // Assumindo que a store de câmera existe
import { useAuthStore } from '../stores/authStore';
import { Video, VideoOff } from 'lucide-react';

interface CameraListProps {
  onViewCamera: (camera: { id: number; name: string }) => void;
}

const CameraList: React.FC<CameraListProps> = ({ onViewCamera }) => {
  const { cameras } = useCameraStore(); // Pega as câmeras da store
  const { token } = useAuthStore(); // Pega o token para autenticar o request da imagem
  const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/api\/v1$/, '');

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {cameras.map((camera) => (
        <div
          key={camera.id}
          className="bg-white rounded-lg shadow-sm overflow-hidden cursor-pointer transition-all duration-300 hover:shadow-lg hover:-translate-y-1"
          className="bg-white rounded-lg shadow-sm overflow-hidden cursor-pointer transition-all duration-300 hover:shadow-lg hover:-translate-y-1 relative"
          onClick={() => onViewCamera({ id: camera.id, name: camera.name })}
        >
          <div className={`aspect-video flex items-center justify-center text-white bg-black`}>
            {camera.is_active ? (
              // Mostra a imagem do thumbnail se a câmera estiver ativa
              <img
                src={`${apiBaseUrl}/api/v1/cameras/${camera.id}/thumbnail?token=${token}`}
                src={camera.thumbnail_url || '/placeholder-video.png'} // Usa thumbnail_url ou um placeholder
                alt={`Preview da ${camera.name}`}
                className="w-full h-full object-cover"
                // Fallback para um ícone caso a imagem não carregue
                onError={(e) => { e.currentTarget.outerHTML = '<div class="flex items-center justify-center w-full h-full bg-slate-800"><svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-red-500"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"></path><circle cx="12" cy="13" r="3"></circle></svg></div>'; }}
              />
            ) : (
              // Mostra o ícone de câmera desligada se estiver inativa
              <VideoOff className="w-12 h-12 text-gray-500" />
            )}
          </div>
          <div className="p-4">
            <div className="flex justify-between items-center">
              <h3 className="font-bold text-gray-800 truncate">{camera.name}</h3>
              <div className={`flex items-center text-xs px-2 py-1 rounded-full ${camera.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                {camera.is_active ? <Video className="w-3 h-3 mr-1" /> : <VideoOff className="w-3 h-3 mr-1" />}
                {camera.is_active ? 'Ativa' : 'Inativa'}
              </div>
            </div>
            <p className="text-sm text-gray-500 truncate" title={camera.rtsp_url}>{camera.rtsp_url}</p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default CameraList;