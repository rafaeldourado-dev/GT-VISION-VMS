import React, { useState, useEffect, useRef } from 'react';
import { X, Video, WifiOff } from 'lucide-react';
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
  const [frameSrc, setFrameSrc] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);
  const { token } = useAuthStore.getState();

  useEffect(() => {
    if (!camera || !token) {
      return;
    }

    // Constrói a URL do WebSocket para o backend no Docker
    const wsUrl = `ws://127.0.0.1:8000/ws/stream/${camera.id}?token=${token}`;
    
    socketRef.current = new WebSocket(wsUrl);

    socketRef.current.onopen = () => {
      console.log('WebSocket conectado para a câmara:', camera.name);
      setIsConnected(true);
    };

    socketRef.current.onmessage = (event) => {
      if (event.data instanceof Blob) {
        if (frameSrc) URL.revokeObjectURL(frameSrc);
        const url = URL.createObjectURL(event.data);
        setFrameSrc(url);
      }
    };

    socketRef.current.onclose = () => {
      console.log('WebSocket desconectado.');
      setIsConnected(false);
    };

    socketRef.current.onerror = (error) => {
      console.error('Erro no WebSocket:', error);
      setIsConnected(false);
    };

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
      if (frameSrc) {
        URL.revokeObjectURL(frameSrc);
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
        <div className="p-4 bg-black aspect-video flex items-center justify-center">
          {isConnected && frameSrc ? (
            <img src={frameSrc} alt={`Stream da ${camera.name}`} className="w-full h-full object-contain" />
          ) : (
            <div className="text-white text-center">
              <div className="animate-pulse">
                <WifiOff className="w-16 h-16 text-gray-500 mx-auto mb-4" />
              </div>
              <p className="font-semibold">{isConnected ? "A aguardar frames..." : "A conectar ao stream..."}</p>
              <p className="text-sm text-gray-400">Verifique se a câmara está online e a URL RTSP está correta.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VideoStreamModal;