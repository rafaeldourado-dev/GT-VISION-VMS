import React, { useEffect, useState } from 'react';
import { Plus, Trash2, Camera, Eye, CheckCircle } from 'lucide-react';
import { useCameraStore } from '../stores/cameraStore';
import AddCameraModal from '../components/AddCameraModal';
import VideoStreamModal from '../components/VideoStreamModal';
import AppLayout from '../components/AppLayout';

const StatCard: React.FC<{ title: string; value: string | number; icon: React.ReactNode }> = ({ title, value, icon }) => (
  <div className="bg-white p-6 rounded-lg shadow-sm flex items-center">
    {icon}
    <div className="ml-4">
      <p className="text-sm font-medium text-gray-600">{title}</p>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  </div>
);

const Dashboard: React.FC = () => {
  const { cameras, isLoading, fetchCameras, deleteCamera } = useCameraStore();
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [deletingCameraId, setDeletingCameraId] = useState<number | null>(null);
  const [viewingCamera, setViewingCamera] = useState<{id: number, name: string} | null>(null);

  useEffect(() => {
    fetchCameras();
  }, [fetchCameras]);

  const handleDeleteCamera = async (cameraId: number) => {
    if (window.confirm('Tem certeza que deseja excluir esta câmera?')) {
      setDeletingCameraId(cameraId);
      await deleteCamera(cameraId);
      setDeletingCameraId(null);
    }
  };

  return (
    <AppLayout>
      <div className="mb-8">
          <div className="flex justify-between items-center flex-wrap gap-4">
              <div>
                  <h2 className="text-3xl font-bold text-gray-900">Dashboard de Câmaras</h2>
                  <p className="text-gray-600 mt-1">Gira as suas câmaras e visualize os streams.</p>
              </div>
              <button onClick={() => setIsAddModalOpen(true)} className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 shadow-sm hover:shadow-md transition-all transform hover:-translate-y-0.5">
                  <Plus className="w-4 h-4 mr-2" /> Adicionar Câmara
              </button>
          </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <StatCard title="Total de Câmaras" value={cameras.length} icon={<Camera className="w-8 h-8 text-blue-600" />} />
        {/* Este card pode ser alterado para mostrar câmaras ativas vs inativas */}
        <StatCard title="Câmaras Ativas" value={cameras.filter(c => c.is_active).length} icon={<Eye className="w-8 h-8 text-green-600" />} />
        <StatCard title="Status do Sistema" value="Online" icon={<CheckCircle className="w-8 h-8 text-green-600" />} />
      </div>

      {isLoading ? (
          <div className="p-8 text-center bg-white rounded-lg"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div><p className="mt-2 text-gray-600">A carregar câmaras...</p></div>
      ) : cameras.length === 0 ? (
          <div className="p-8 text-center bg-white rounded-lg shadow-sm"><Camera className="w-12 h-12 text-gray-400 mx-auto mb-4" /><h3 className="text-lg font-medium text-gray-900 mb-2">Nenhuma câmara registada</h3><p className="text-gray-600 mb-4">Comece por adicionar a sua primeira câmara</p><button onClick={() => setIsAddModalOpen(true)} className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-all transform hover:-translate-y-0.5"><Plus className="w-4 h-4 mr-2" />Adicionar Primeira Câmara</button></div>
      ) : (
        <div className="bg-white shadow-sm rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nome</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">URL RTSP</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {cameras.map((camera) => (
                  <tr key={camera.id} className="hover:bg-blue-50/50 transition-colors duration-150 even:bg-gray-50/50">
                    <td className="px-6 py-4 text-sm font-medium text-gray-500">#{camera.id}</td>
                    <td className="px-6 py-4">
                        <div className="flex items-center">
                            <Camera className="w-4 h-4 text-gray-400 mr-3" />
                            <span className="text-sm font-medium text-gray-800">{camera.name}</span>
                        </div>
                    </td>
                    <td className="px-6 py-4"><span className="text-sm text-gray-600 font-mono bg-gray-100 px-2 py-1 rounded">{camera.rtsp_url}</span></td>
                    <td className="px-6 py-4 text-sm flex items-center gap-2">
                      <button onClick={() => setViewingCamera({ id: camera.id, name: camera.name })} className="inline-flex items-center px-3 py-1 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-md transition-colors">
                        <Eye className="w-4 h-4 mr-1" /> Visualizar
                      </button>
                      <button onClick={() => handleDeleteCamera(camera.id)} disabled={deletingCameraId === camera.id} className="inline-flex items-center px-3 py-1 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-md disabled:opacity-50 transition-colors">
                        {deletingCameraId === camera.id ? <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-600 mr-2"></div> : <Trash2 className="w-4 h-4 mr-1" />} Excluir
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      <AddCameraModal isOpen={isAddModalOpen} onClose={() => setIsAddModalOpen(false)} />
      <VideoStreamModal camera={viewingCamera} onClose={() => setViewingCamera(null)} />
    </AppLayout>
  );
};

export default Dashboard;