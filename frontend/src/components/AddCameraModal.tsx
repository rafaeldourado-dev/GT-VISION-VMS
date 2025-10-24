import React, { useState, useEffect } from 'react';
import { useCameraStore } from '../stores/cameraStore';
import { X, Camera, Save } from 'lucide-react';

interface CameraData {
  id?: number;
  name: string;
  rtsp_url: string;
  latitude?: number | null;
  longitude?: number | null;
}

interface AddCameraModalProps {
  isOpen: boolean;
  onClose: () => void;
  cameraToEdit?: CameraData | null;
}

const AddCameraModal: React.FC<AddCameraModalProps> = ({ isOpen, onClose, cameraToEdit }) => {
  const [name, setName] = useState('');
  const [rtspUrl, setRtspUrl] = useState('');
  const [latitude, setLatitude] = useState<string>('');
  const [longitude, setLongitude] = useState<string>('');
  const { addCamera, updateCamera } = useCameraStore();

  useEffect(() => {
    if (cameraToEdit) {
      setName(cameraToEdit.name);
      setRtspUrl(cameraToEdit.rtsp_url);
      setLatitude(cameraToEdit.latitude?.toString() ?? '');
      setLongitude(cameraToEdit.longitude?.toString() ?? '');
    } else {
      // Reset form when opening for a new camera
      setName('');
      setRtspUrl('');
      setLatitude('');
      setLongitude('');
    }
  }, [cameraToEdit, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const cameraData = {
      name,
      rtsp_url: rtspUrl,
      latitude: latitude ? parseFloat(latitude) : null,
      longitude: longitude ? parseFloat(longitude) : null,
    };

    let success = false;
    if (cameraToEdit) {
      // Lógica de atualização
      success = await updateCamera(cameraToEdit.id!, cameraData);
    } else {
      // Lógica de adição
      success = await addCamera(cameraData);
    }

    if (success) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-800 flex items-center">
            <Camera className="w-6 h-6 mr-2" />
            {cameraToEdit ? 'Editar Câmera' : 'Adicionar Nova Câmera'}
          </h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-800">
            <X className="w-6 h-6" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Nome da Câmera</label>
            <input type="text" value={name} onChange={(e) => setName(e.target.value)} required className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">URL RTSP</label>
            <input type="text" value={rtspUrl} onChange={(e) => setRtspUrl(e.target.value)} required className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" placeholder="rtsp://..." />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Latitude</label>
              <input type="number" step="any" value={latitude} onChange={(e) => setLatitude(e.target.value)} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Longitude</label>
              <input type="number" step="any" value={longitude} onChange={(e) => setLongitude(e.target.value)} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" />
            </div>
          </div>
          <div className="flex justify-end space-x-3 pt-4">
            <button type="button" onClick={onClose} className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300">
              Cancelar
            </button>
            <button type="submit" className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
              <Save className="w-5 h-5 mr-2" />
              Salvar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddCameraModal;