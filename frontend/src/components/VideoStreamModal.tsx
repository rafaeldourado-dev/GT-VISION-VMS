import React, { useState, useEffect, useRef } from 'react';
import { X, Video, WifiOff, Loader } from 'lucide-react';
import { useAuthStore } from '../stores/authStore';
import { WebRTCPlayer } from '@eyevinn/webrtc-player';

interface Camera {
  id: number;
  name: string;
}

interface VideoStreamModalProps {
  camera: Camera | null;
  onClose: () => void;
}

const VideoStreamModal: React.FC<VideoStreamModalProps> = ({ camera, onClose }) => {
  const videoRef = useRef<HTMLVideoElement>(null); // Alterado para HTMLVideoElement
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { token } = useAuthStore(); // Obtém o token do store

  useEffect(() => {
    if (!camera || !token) {
      setError('Câmera ou token de autenticação não disponíveis.');
      setIsLoading(false);
      return;
    }

    let ws: WebSocket | null = null;
    let player: WebRTCPlayer | null = null;
    
    // Constrói a URL do WebSocket de configuração para o backend
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';
    const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const domain = apiBaseUrl.replace(/^https?:\/\//, '').replace(/\/api\/v1$/, '');
    const configWsUrl = `${wsProtocol}://${domain}/api/v1/streaming/ws/player/${camera.id}?token=${token}`;

    ws = new WebSocket(configWsUrl);

    ws.onopen = () => {
      console.log(`WebSocket de configuração conectado para a câmera: ${camera.name}`);
    };

    ws.onmessage = async (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'webrtc_url' && videoRef.current) {
        console.log(`Recebida URL WebRTC: ${message.url}`);
        try {
          player = new WebRTCPlayer({
            video: videoRef.current,
            type: 'whep',
            url: message.url,
          });
          await player.load();
          setIsLoading(false);
        } catch (e: any) {
          console.error('Erro ao iniciar o player WebRTC', e);
          setError(`Falha ao carregar o stream de vídeo: ${e.message}`);
          setIsLoading(false);
        }
      }
    };

    ws.onerror = (err) => {
      console.error('Erro no WebSocket de configuração:', err);
      setError('Falha ao configurar o stream da câmera.');
      setIsLoading(false);
    };

    ws.onclose = (event) => {
      console.log(`WebSocket de configuração desconectado: ${event.reason}`);
      if (event.code !== 1000) { // 1000 é fechamento normal
        setError(event.reason || 'A conexão com o servidor foi perdida.');
      }
      setIsLoading(false);
    };

    return () => {
      player?.destroy(); // Destrói o player WebRTC
      ws?.close(); // Fecha o WebSocket de configuração
    };
  }, [camera, token]); // Dependências do useEffect

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
            <div className="text-white text-center">
              <Loader color="white" size="xl" className="mx-auto mb-4" />
              <p className="font-semibold">A carregar stream...</p>
            </div>
          ) : (
            <video ref={videoRef} className="w-full h-full object-contain" autoPlay muted playsInline />
          )}
          {error && <div className="absolute inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4"><p className="text-red-500 text-center">{error}</p></div>}
        </div>
      </div>
    </div>
  );
};

export default VideoStreamModal;