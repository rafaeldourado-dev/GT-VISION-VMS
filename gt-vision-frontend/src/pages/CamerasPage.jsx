
import React, { useState, useEffect } from 'react'
import {Plus, Trash2, Eye} from 'lucide-react'
import { camerasService } from '../services/api'
import Modal from '../components/Modal'
import VideoStreamModal from '../components/VideoStreamModal'
import toast from 'react-hot-toast'

const CamerasPage = () => {
  const [cameras, setCameras] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [showStreamModal, setShowStreamModal] = useState(false)
  const [selectedCamera, setSelectedCamera] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    location: '',
    ip_address: '',
    active: true
  })

  useEffect(() => {
    fetchCameras()
  }, [])

  const fetchCameras = async () => {
    try {
      setLoading(true)
      const data = await camerasService.getAll()
      setCameras(data)
    } catch (error) {
      toast.error('Erro ao carregar câmeras')
      console.error('Erro ao buscar câmeras:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddCamera = async (e) => {
    e.preventDefault()
    
    if (!formData.name || !formData.location || !formData.ip_address) {
      toast.error('Por favor, preencha todos os campos obrigatórios')
      return
    }

    try {
      await camerasService.create(formData)
      toast.success('Câmera adicionada com sucesso!')
      setShowAddModal(false)
      setFormData({ name: '', location: '', ip_address: '', active: true })
      fetchCameras()
    } catch (error) {
      toast.error('Erro ao adicionar câmera')
      console.error('Erro ao criar câmera:', error)
    }
  }

  const handleDeleteCamera = async (cameraId) => {
    if (!window.confirm('Tem certeza que deseja excluir esta câmera?')) {
      return
    }

    try {
      await camerasService.delete(cameraId)
      toast.success('Câmera excluída com sucesso!')
      fetchCameras()
    } catch (error) {
      toast.error('Erro ao excluir câmera')
      console.error('Erro ao deletar câmera:', error)
    }
  }

  const handleViewStream = (camera) => {
    setSelectedCamera(camera)
    setShowStreamModal(true)
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Câmeras</h1>
          <p className="mt-1 text-sm text-gray-500">
            Gerencie as câmeras do sistema
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <Plus className="h-4 w-4 mr-2" />
          Adicionar Nova
        </button>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Nome
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Localização
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                IP
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Ações
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan="5" className="px-6 py-4 text-center text-gray-500">
                  Carregando...
                </td>
              </tr>
            ) : cameras.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-4 text-center text-gray-500">
                  Nenhuma câmera cadastrada.
                </td>
              </tr>
            ) : (
              cameras.map((camera) => (
                <tr key={camera.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {camera.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {camera.location}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {camera.ip_address}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      camera.active 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {camera.active ? 'Ativa' : 'Inativa'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                    <button
                      onClick={() => handleViewStream(camera)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      <Eye className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteCamera(camera.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Modal Adicionar Câmera */}
      <Modal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        title="Adicionar Nova Câmera"
      >
        <form onSubmit={handleAddCamera} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Nome *
            </label>
            <input
              type="text"
              required
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Localização *
            </label>
            <input
              type="text"
              required
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              value={formData.location}
              onChange={(e) => setFormData(prev => ({ ...prev, location: e.target.value }))}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Endereço IP *
            </label>
            <input
              type="text"
              required
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              value={formData.ip_address}
              onChange={(e) => setFormData(prev => ({ ...prev, ip_address: e.target.value }))}
            />
          </div>
          
          <div className="flex items-center">
            <input
              type="checkbox"
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              checked={formData.active}
              onChange={(e) => setFormData(prev => ({ ...prev, active: e.target.checked }))}
            />
            <label className="ml-2 block text-sm text-gray-900">
              Câmera ativa
            </label>
          </div>
          
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={() => setShowAddModal(false)}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
            >
              Adicionar
            </button>
          </div>
        </form>
      </Modal>

      {/* Modal Stream */}
      <VideoStreamModal
        isOpen={showStreamModal}
        onClose={() => setShowStreamModal(false)}
        camera={selectedCamera}
      />
    </div>
  )
}

export default CamerasPage
