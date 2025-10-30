import React from 'react';
import { Camera } from '../types'; // Assumindo que Camera type é definido em types.ts

interface StreamModalProps {
  isOpen: boolean;
  onClose: () => void;
  camera: Camera | null;
  token: string | null; // Token JWT para autenticação, se necessário para o stream
}

const StreamModal: React.FC<StreamModalProps> = ({ isOpen, onClose, camera, token }) => {
  if (!isOpen || !camera) {
    return null;
  }

  // URL do stream WebRTC do MediaMTX.
  // O MediaMTX geralmente expõe WebRTC via WebSocket em ws://<host>:<webrtc_port>/<path_name>/webrtc
  // O <path_name> é o ID da câmera no nosso caso.
  // Para desenvolvimento local, o host pode ser 'localhost' ou o IP do contêiner MediaMTX.
  // A porta 8889 é a porta WebRTC exposta no docker-compose.yml.
  // Se o backend precisar autenticar o acesso ao MediaMTX, o token pode ser passado via WebSocket.
  const webrtcWsUrl = `ws://localhost:8889/${camera.id}/webrtc`;

  return (
    <div
      className="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg shadow-xl p-6 w-11/12 md:w-2/3 lg:w-1/2 max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()} // Impede que o modal feche ao clicar dentro
      >
        <div className="flex justify-between items-center border-b pb-3 mb-4">
          <h3 className="text-xl font-semibold text-gray-900">Visualizando Stream: {camera.name}</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 focus:outline-none"
          >
            <svg
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <div className="mb-4">
          <p className="text-gray-700 mb-2">RTSP URL: <span className="font-mono text-sm">{camera.rtsp_url}</span></p>
          <div className="w-full bg-black flex items-center justify-center aspect-video rounded-md">
            <p className="text-white text-lg">Placeholder para o Stream WebRTC</p>
            <p className="text-gray-400 text-sm mt-2">
              (A integração com um player WebRTC para {webrtcWsUrl} seria feita aqui, possivelmente usando o token fornecido para autenticação.)
            </p>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 focus:outline-none"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
};

export default StreamModal;