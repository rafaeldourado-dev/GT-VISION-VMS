
import React, { useState } from 'react'
import Modal from './Modal'
import {AlertTriangle} from 'lucide-react'

const VideoStreamModal = ({ isOpen, onClose, camera }) => {
  const [imageError, setImageError] = useState(false)
  const [imageLoading, setImageLoading] = useState(true)

  const handleImageLoad = () => {
    setImageLoading(false)
    setImageError(false)
  }

  const handleImageError = () => {
    setImageLoading(false)
    setImageError(true)
  }

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={onClose} 
      title={`Stream - ${camera?.name || 'Câmera'}`}
      size="xl"
    >
      <div className="space-y-4">
        <div className="bg-gray-100 rounded-lg overflow-hidden">
          {imageLoading && (
            <div className="flex items-center justify-center h-64 bg-gray-200">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-2 text-gray-600">Carregando stream...</span>
            </div>
          )}
          
          {imageError && (
            <div className="flex flex-col items-center justify-center h-64 bg-gray-100 text-gray-500">
              <AlertTriangle className="h-12 w-12 mb-2" />
              <p>Erro ao carregar o stream da câmera</p>
              <p className="text-sm">Verifique se a câmera está online</p>
            </div>
          )}
          
          {camera && (
            <img
              src={`http://localhost:8000/cameras/${camera.id}/stream`}
              alt={`Stream da ${camera.name}`}
              className={`w-full h-auto ${imageLoading || imageError ? 'hidden' : 'block'}`}
              onLoad={handleImageLoad}
              onError={handleImageError}
            />
          )}
        </div>
        
        {camera && (
          <div className="text-sm text-gray-600">
            <p><strong>Localização:</strong> {camera.location || 'Não informada'}</p>
            <p><strong>Status:</strong> {camera.active ? 'Ativa' : 'Inativa'}</p>
          </div>
        )}
      </div>
    </Modal>
  )
}

export default VideoStreamModal
