import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { useCameraStore } from '../stores/cameraStore';
import { Eye, MapPin } from 'lucide-react';

// Solução padrão para corrigir o problema de ícones do Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Componente auxiliar para ajustar os limites do mapa automaticamente
const AutoFitBounds: React.FC<{ bounds: L.LatLngBounds | null }> = ({ bounds }) => {
  const map = useMap();
  useEffect(() => {
    if (bounds && bounds.isValid() && Object.keys(bounds).length > 0) {
      // Adiciona um padding para que os marcadores não fiquem nas bordas
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [map, bounds]);
  return null; // Este componente não renderiza nada no DOM
};

interface MapDisplayProps {
  onViewCamera: (camera: { id: number; name: string }) => void;
}

const MapDisplay: React.FC<MapDisplayProps> = ({ onViewCamera }) => {
  const { cameras } = useCameraStore();
  const camerasWithCoords = cameras.filter(
    (c) => c.latitude != null && c.longitude != null
  );

  // Calcula os limites (bounds) que englobam todas as câmeras
  const bounds = camerasWithCoords.length > 0
    ? L.latLngBounds(camerasWithCoords.map(c => [c.latitude!, c.longitude!]))
    : null;

  // Define um centro padrão caso não haja câmeras
  const defaultCenter: L.LatLngExpression = [-15.7801, -47.9292];

  return (
    <div className="bg-white shadow-sm rounded-lg overflow-hidden h-[70vh]">
      <MapContainer
        center={defaultCenter}
        zoom={4}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        <AutoFitBounds bounds={bounds} />
        {camerasWithCoords.map((camera) => (
          <Marker
            key={camera.id}
            position={[camera.latitude!, camera.longitude!]}
          >
            <Popup>
              <div className="font-semibold">{camera.name}</div>
              <div className="flex flex-col space-y-2 mt-2">
                <button
                  onClick={() => onViewCamera({ id: camera.id, name: camera.name })}
                  className="w-full flex items-center justify-center px-3 py-1 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md transition-colors text-sm"
                >
                  <Eye className="w-4 h-4 mr-1" />
                  Visualizar Stream
                </button>
                <a
                  href={`https://www.google.com/maps/dir/?api=1&destination=${camera.latitude},${camera.longitude}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full flex items-center justify-center px-3 py-1 text-green-600 hover:text-green-800 hover:bg-green-50 rounded-md transition-colors text-sm"
                >
                  <MapPin className="w-4 h-4 mr-1" />
                  Como Chegar
                </a>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};

export default MapDisplay;  