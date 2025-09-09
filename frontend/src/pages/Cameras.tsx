import React, { useState, useEffect } from 'react';
import {Plus, Camera, MapPin, Activity} from 'lucide-react';
import { Dialog } from '@headlessui/react';
import api from '../config/api';
import toast from 'react-hot-toast';

interface CameraData {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  rtsp_url: string; // Adicionei este campo
  is_active: boolean;
}

const Cameras: React.FC = () => {
  const [cameras, setCameras] = useState<CameraData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    rtsp_url: '', // Adicionei este campo
    latitude: '',
    longitude: '',
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
      toast.error('Erro ao carregar câmeras');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const payload = {
        name: formData.name,
        rtsp_url: formData.rtsp_url, // Use o novo campo
        latitude: parseFloat(formData.latitude),
        longitude: parseFloat(formData.longitude),
      };

      const response = await api.post('/cameras/', payload);
      setCameras([...cameras, response.data]);
      setShowAddModal(false);
      setFormData({ name: '', rtsp_url: '', latitude: '', longitude: '' }); // Limpe o novo campo
      toast.success('Câmera adicionada com sucesso!');
    } catch (error: any) {
      console.error('Erro ao adicionar câmera:', error);
      if (error.response?.status === 400) {
        toast.error('Dados inválidos. Verifique as coordenadas.');
      } else {
        toast.error('Erro ao adicionar câmera');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setFormData({ name: '', rtsp_url: '', latitude: '', longitude: '' });
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gerenciamento de Câmeras</h1>
          <p className="mt-2 text-gray-600">Configure e monitore suas câmeras de vigilância</p>
        </div>
        <button
          onClick={() => {
            resetForm();
            setShowAddModal(true);
          }}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="h-5 w-5 mr-2" />
          Adicionar Câmera
        </button>
      </div>

      {/* Lista de Câmeras */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Câmeras Cadastradas</h2>
        </div>
        
        {cameras.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Nome
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Coordenadas
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {cameras.map((camera) => (
                  <tr key={camera.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <Camera className="h-5 w-5 text-gray-400 mr-3" />
                        <div>
                          <div className="text-sm font-medium text-gray-900">{camera.name}</div>
                          <div className="text-sm text-gray-500">ID: {camera.id}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center text-sm text-gray-900">
                        <MapPin className="h-4 w-4 text-gray-400 mr-2" />
                        {camera.latitude.toFixed(6)}, {camera.longitude.toFixed(6)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <Activity className={`h-4 w-4 mr-2 ${camera.is_active ? 'text-green-500' : 'text-red-500'}`} />
                        <span className={`text-sm font-medium ${camera.is_active ? 'text-green-800' : 'text-red-800'}`}>
                          {camera.is_active ? 'Ativa' : 'Inativa'}
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12">
            <Camera className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Nenhuma câmera cadastrada</h3>
            <p className="text-gray-600 mb-4">Comece adicionando sua primeira câmera ao sistema</p>
            <button
              onClick={() => {
                resetForm();
                setShowAddModal(true);
              }}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="h-5 w-5 mr-2" />
              Adicionar Primeira Câmera
            </button>
          </div>
        )}
      </div>

      {/* Modal Adicionar Câmera */}
      <Dialog
        open={showAddModal}
        onClose={() => setShowAddModal(false)}
        className="relative z-50"
      >
        <div className="fixed inset-0 bg-black/25" />
        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Dialog.Panel className="w-full max-w-md bg-white rounded-lg shadow-xl">
              <div className="px-6 py-4 border-b border-gray-200">
                <Dialog.Title className="text-lg font-semibold text-gray-900">
                  Adicionar Nova Câmera
                </Dialog.Title>
              </div>
              
              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                    Nome da Câmera
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    required
                    value={formData.name}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Ex: CAM-01 Entrada Principal"
                  />
                </div>

                <div>
                  <label htmlFor="rtsp_url" className="block text-sm font-medium text-gray-700 mb-1">
                    URL RTSP
                  </label>
                  <input
                    type="text"
                    id="rtsp_url"
                    name="rtsp_url"
                    required
                    value={formData.rtsp_url}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                    placeholder="rtsp://user:pass@ip:port/stream"
                  />
                </div>

                <div>
                  <label htmlFor="latitude" className="block text-sm font-medium text-gray-700 mb-1">
                    Latitude
                  </label>
                  <input
                    type="number"
                    id="latitude"
                    name="latitude"
                    required
                    step="any"
                    value={formData.latitude}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                    placeholder="-23.5505"
                  />
                </div>

                <div>
                  <label htmlFor="longitude" className="block text-sm font-medium text-gray-700 mb-1">
                    Longitude
                  </label>
                  <input
                    type="number"
                    id="longitude"
                    name="longitude"
                    required
                    step="any"
                    value={formData.longitude}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                    placeholder="-46.6333"
                  />
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowAddModal(false)}
                    className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {isSubmitting ? 'Adicionando...' : 'Adicionar'}
                  </button>
                </div>
              </form>
            </Dialog.Panel>
          </div>
        </div>
      </Dialog>
    </div>
  );
};

export default Cameras;