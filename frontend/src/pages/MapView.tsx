import React, { useState, useEffect } from 'react';
import Map, { Marker, Popup } from 'react-map-gl';
import {Camera, Eye} from 'lucide-react';
import api from '../config/api';
import { Dialog } from '@headlessui/react';

// Substitua pela sua chave do Mapbox
const MAPBOX_TOKEN = 'pk.eyJ1IjoiZXhhbXBsZSIsImEiOiJjbGV4YW1wbGUifQ.example';

interface CameraData {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  is_active: boolean;
}

interface Sighting {
  id: number;
  license_plate: string;
  timestamp: string;
  camera_id: number;
}

const MapView: React.FC = () => {
  const [cameras, setCameras] = useState<CameraData[]>([]);
  const [selectedCamera, setSelectedCamera] = useState<CameraData | null>(null);
  const [cameraSightings, setCameraSightings] = useState<Sighting[]>([]);
  const [showSightingsModal, setShowSightingsModal] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [sightingsLoading, setSightingsLoading] = useState(false);

  const [viewState, setViewState] = useState({
    longitude: -46.6333,
    latitude: -23.5505,
    zoom: 10
  });

  useEffect(() => {
    loadCameras();
  }, []);

  const loadCameras = async () => {
    try {
      setIsLoading(true);
      const response = await api.get('/cameras/');
      setCameras(response.data);
    } catch (error) {
      console.error('Erro ao carregar câmeras:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadCameraSightings = async (cameraId: number) => {
    try {
      setSightingsLoading(true);
      const response = await api.get(`/sightings/camera/${cameraId}`);
      setCameraSightings(response.data);
      setShowSightingsModal(true);
    } catch (error) {
      console.error('Erro ao carregar avistamentos da câmera:', error);
    } finally {
      setSightingsLoading(false);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('pt-BR');
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Mapa de Câmeras</h1>
        <p className="mt-2 text-gray-600">Visualize a localização das câmeras e seus avistamentos</p>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div style={{ height: '600px' }}>
          {MAPBOX_TOKEN !== 'pk.eyJ1IjoiZXhhbXBsZSIsImEiOiJjbGV4YW1wbGUifQ.example' ? (
            <Map
              {...viewState}
              onMove={evt => setViewState(evt.viewState)}
              mapboxAccessToken={MAPBOX_TOKEN}
              style={{ width: '100%', height: '100%' }}
              mapStyle="mapbox://styles/mapbox/streets-v12"
            >
              {cameras.map((camera) => (
                <Marker
                  key={camera.id}
                  longitude={camera.longitude}
                  latitude={camera.latitude}
                  anchor="bottom"
                >
                  <button
                    onClick={() => setSelectedCamera(camera)}
                    className={`p-2 rounded-full shadow-lg transition-colors ${
                      camera.is_active
                        ? 'bg-green-500 hover:bg-green-600'
                        : 'bg-red-500 hover:bg-red-600'
                    }`}
                  >
                    <Camera className="h-5 w-5 text-white" />
                  </button>
                </Marker>
              ))}

              {selectedCamera && (
                <Popup
                  longitude={selectedCamera.longitude}
                  latitude={selectedCamera.latitude}
                  anchor="top"
                  onClose={() => setSelectedCamera(null)}
                  closeButton={true}
                  closeOnClick={false}
                >
                  <div className="p-3">
                    <h3 className="font-semibold text-gray-900">{selectedCamera.name}</h3>
                    <p className={`text-sm ${selectedCamera.is_active ? 'text-green-600' : 'text-red-600'}`}>
                      {selectedCamera.is_active ? 'Ativa' : 'Inativa'}
                    </p>
                    <button
                      onClick={() => loadCameraSightings(selectedCamera.id)}
                      className="mt-2 w-full bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 transition-colors"
                    >
                      Ver Avistamentos
                    </button>
                  </div>
                </Popup>
              )}
            </Map>
          ) : (
            <div className="h-full flex items-center justify-center bg-gray-100">
              <div className="text-center">
                <Camera className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Configuração do Mapbox Necessária</h3>
                <p className="text-gray-600 mb-4">
                  Para visualizar o mapa, configure sua chave de API do Mapbox na variável MAPBOX_TOKEN
                </p>
                <div className="bg-white rounded-lg shadow p-6 max-w-md mx-auto">
                  <h4 className="font-semibold text-gray-900 mb-4">Câmeras Cadastradas:</h4>
                  <div className="space-y-2">
                    {cameras.map((camera) => (
                      <div key={camera.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <div>
                          <p className="font-medium">{camera.name}</p>
                          <p className="text-sm text-gray-600">
                            {camera.latitude.toFixed(4)}, {camera.longitude.toFixed(4)}
                          </p>
                        </div>
                        <div className={`w-3 h-3 rounded-full ${camera.is_active ? 'bg-green-500' : 'bg-red-500'}`} />
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Modal de Avistamentos */}
      <Dialog
        open={showSightingsModal}
        onClose={() => setShowSightingsModal(false)}
        className="relative z-50"
      >
        <div className="fixed inset-0 bg-black/25" />
        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Dialog.Panel className="w-full max-w-2xl bg-white rounded-lg shadow-xl">
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <Dialog.Title className="text-lg font-semibold text-gray-900">
                    Avistamentos - {selectedCamera?.name}
                  </Dialog.Title>
                  <button
                    onClick={() => setShowSightingsModal(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ✕
                  </button>
                </div>
              </div>
              
              <div className="p-6">
                {sightingsLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                  </div>
                ) : cameraSightings.length > 0 ? (
                  <div className="space-y-3">
                    {cameraSightings.map((sighting) => (
                      <div key={sighting.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center">
                          <Eye className="h-5 w-5 text-blue-600 mr-3" />
                          <div>
                            <p className="font-medium text-gray-900">{sighting.license_plate}</p>
                            <p className="text-sm text-gray-600">{formatTimestamp(sighting.timestamp)}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Eye className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">Nenhum avistamento encontrado para esta câmera</p>
                  </div>
                )}
              </div>
            </Dialog.Panel>
          </div>
        </div>
      </Dialog>
    </div>
  );
};

export default MapView;