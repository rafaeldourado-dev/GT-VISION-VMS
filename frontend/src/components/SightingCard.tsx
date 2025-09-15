import React from 'react';
import { Clock, Video, Tag } from 'lucide-react';

interface Sighting {
  id: number;
  license_plate: string;
  image_path: string | null;
  timestamp: string;
  camera: {
    name: string;
  };
}

interface SightingCardProps {
  sighting: Sighting;
}

const API_BASE_URL = 'http://127.0.0.1:8000';

const formatDateTime = (isoString: string) => {
  if (!isoString) return 'N/A';
  return new Date(isoString).toLocaleString('pt-BR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  });
};

const SightingCard: React.FC<SightingCardProps> = ({ sighting }) => {
  const imageUrl = sighting.image_path ? `${API_BASE_URL}/captures/${sighting.image_path}` : 'https://via.placeholder.com/400x200?text=Imagem+N/D';

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col overflow-hidden transition-all duration-300 hover:shadow-md hover:-translate-y-1">
      <div className="bg-gray-200">
        <img 
          src={imageUrl} 
          alt={`Veículo com placa ${sighting.license_plate}`} 
          className="w-full h-48 object-cover"
          onError={(e) => { e.currentTarget.src = 'https://via.placeholder.com/400x200?text=Imagem+N/D'; }}
        />
      </div>
      <div className="p-4 flex-grow flex flex-col">
        <div className="flex items-center gap-2 mb-3">
            <Tag className="w-5 h-5 text-blue-600" />
            <span className="text-xl font-bold text-gray-800 font-mono tracking-wider">{sighting.license_plate}</span>
        </div>
        <div className="space-y-2 text-sm text-gray-600">
          <div className="flex items-center">
            <Video className="w-4 h-4 mr-2" />
            <span>{sighting.camera.name}</span>
          </div>
          <div className="flex items-center">
            <Clock className="w-4 h-4 mr-2" />
            <span>{formatDateTime(sighting.timestamp)}</span>
          </div>
        </div>
        <div className="mt-4 pt-4 border-t border-gray-100">
            <a href="#" className="text-blue-600 hover:text-blue-800 font-semibold text-sm">
                Ver detalhes
            </a>
        </div>
      </div>
    </div>
  );
};

export default SightingCard;