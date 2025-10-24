import React, { useEffect, useRef } from 'react';
import { useAuthStore } from '../stores/authStore';
import toast from 'react-hot-toast';
import { ShieldAlert } from 'lucide-react';

const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { token, isAuthenticated } = useAuthStore();
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (isAuthenticated && token) {
      // Constrói a URL do WebSocket
      const wsUrl = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1')
        .replace(/^http/, 'ws') // Troca http/https por ws/wss
        .replace('/api/v1', ''); // Remove o sufixo da API

      const connect = () => {
        ws.current = new WebSocket(`${wsUrl}/ws/notifications?token=${token}`);

        ws.current.onopen = () => {
          console.log('WebSocket de notificações conectado.');
        };

        ws.current.onmessage = (event) => {
          const data = JSON.parse(event.data);

          if (data.type === 'blacklist_alert') {
            toast.custom(
              (t) => (
                <div
                  className={`${
                    t.visible ? 'animate-enter' : 'animate-leave'
                  } max-w-md w-full bg-white shadow-lg rounded-lg pointer-events-auto flex ring-1 ring-black ring-opacity-5`}
                >
                  <div className="flex-1 w-0 p-4">
                    <div className="flex items-start">
                      <div className="flex-shrink-0 pt-0.5 text-red-500">
                        <ShieldAlert className="h-8 w-8" />
                      </div>
                      <div className="ml-3 flex-1">
                        <p className="text-sm font-medium text-gray-900">Alerta de Lista Negra!</p>
                        <p className="mt-1 text-sm text-gray-600">
                          Placa <strong>{data.plate}</strong> detectada na câmera <strong>{data.camera_name}</strong>.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ),
              { duration: 10000 } // A notificação fica visível por 10 segundos
            );
          }
        };

        ws.current.onclose = () => {
          console.log('WebSocket de notificações desconectado. Tentando reconectar em 5s...');
          setTimeout(connect, 5000);
        };
      };

      connect();

      return () => {
        if (ws.current) {
          ws.current.close();
        }
      };
    }
  }, [isAuthenticated, token]);

  return <>{children}</>;
};

export default NotificationProvider;