import React, { useState, useEffect, useRef } from 'react';
import { X, Video, Loader, WifiOff } from 'lucide-react';
import { useAuthStore } from '../stores/authStore';

interface Camera {
  id: number;
  name: string;
}

interface VideoStreamModalProps {
  camera: Camera | null;
  onClose: () => void;
}

const VideoStreamModal: React.FC<VideoStreamModalProps> = ({ camera, onClose }) => {
  // Estado para armazenar a URL do frame da imagem
  const [imageSrc, setImageSrc] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { token } = useAuthStore();
  // Ref para manter a URL do objeto anterior e evitar memory leaks
  const prevImageSrcRef = useRef<string | null>(null);

  useEffect(() => {
    if (!camera || !token) {
      return;
    }

    // Reseta os estados ao mudar de câmera
    setIsLoading(true);
    setError(null);
    setImageSrc(null);

    let ws: WebSocket | null = null;

    // Constrói a URL do WebSocket para o backend (OpenCV/JPEG stream)
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';
    const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const domain = apiBaseUrl.replace(/^https?:\/\//, '').replace(/\/api\/v1$/, '');
    // --- CORREÇÃO DA URL DO WEBSOCKET ---
    const wsUrl = `${wsProtocol}://${domain}/ws/stream/${camera.id}?token=${token}`;

    ws = new WebSocket(wsUrl);
    ws.binaryType = 'blob'; // Importante para receber os bytes da imagem como Blob

    ws.onopen = () => {
      console.log(`WebSocket conectado para a câmera: ${camera.name}`);
    };

    ws.onmessage = (event) => {
      // Cria uma URL temporária para o Blob da imagem recebida
      const newImageSrc = URL.createObjectURL(event.data);

      // Limpa a URL do objeto anterior para evitar vazamento de memória
      if (prevImageSrcRef.current) {
        URL.revokeObjectURL(prevImageSrcRef.current);
      }

      setImageSrc(newImageSrc);
      prevImageSrcRef.current = newImageSrc;
      setIsLoading(false); // Para de carregar no primeiro frame recebido
    };

    ws.onerror = (err) => {
      console.error('Erro no WebSocket:', err);
      setError('Falha na conexão com o stream da câmera.');
      setIsLoading(false);
    };

    ws.onclose = (event) => {
      console.log(`WebSocket desconectado: ${event.reason} (Código: ${event.code})`);
      setError(event.reason || 'A conexão com o stream foi perdida.');
    };

    return () => {
      ws?.close();
      // Limpa a última URL de objeto quando o componente é desmontado
      if (prevImageSrcRef.current) {
        URL.revokeObjectURL(prevImageSrcRef.current);
      }
    };
  }, [camera, token]);

  if (!camera) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-xl font-semibold text-gray-800 flex items-center gap-2">
            <Video className="w-5 h-5" />
            {camera.name}
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-4 bg-black aspect-video flex items-center justify-center relative">
          {isLoading ? (
            <div className="text-white text-center flex flex-col items-center">
              <Loader className="w-10 h-10 animate-spin mb-4" />
              <p className="font-semibold">A conectar ao stream...</p>
            </div>
          ) : imageSrc ? (
            <img src={imageSrc} alt={`Stream da ${camera.name}`} className="w-full h-full object-contain" />
          ) : null}
          {error && (
            <div className="absolute inset-0 bg-black bg-opacity-75 flex flex-col items-center justify-center p-4">
              <WifiOff className="w-12 h-12 text-red-500 mb-4" />
              <p className="text-red-400 text-center font-semibold">Falha no Stream</p>
              <p className="text-red-500 text-center text-sm mt-1">{error}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VideoStreamModal;