import React, { useState } from 'react'
import { X, Camera, Link, MapPin } from 'lucide-react'
import { useCameraStore } from '../stores/cameraStore'

interface AddCameraModalProps {
  isOpen: boolean
  onClose: () => void
}

const AddCameraModal: React.FC<AddCameraModalProps> = ({ isOpen, onClose }) => {
  const [name, setName] = useState('')
  const [rtspUrl, setRtspUrl] = useState('')
  const [latitude, setLatitude] = useState('')
  const [longitude, setLongitude] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { addCamera } = useCameraStore()

  const clearForm = () => {
    setName('')
    setRtspUrl('')
    setLatitude('')
    setLongitude('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim() || !rtspUrl.trim()) return

    setIsSubmitting(true)
    const cameraData = {
      name: name.trim(),
      rtsp_url: rtspUrl.trim(),
      latitude: latitude ? parseFloat(latitude) : undefined,
      longitude: longitude ? parseFloat(longitude) : undefined,
    }
    const success = await addCamera(cameraData)
    setIsSubmitting(false)

    if (success) {
      clearForm()
      onClose()
    }
  }
  
  const handleClose = () => {
    clearForm()
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-800 flex items-center gap-2">
            <Camera className="w-5 h-5" /> Adicionar Câmera
          </h2>
          <button onClick={handleClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-5 h-5" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="p-6">
          <div className="space-y-4">
            <div>
              <label htmlFor="camera-name" className="block text-sm font-medium text-gray-700 mb-1">Nome da Câmera</label>
              <div className="relative">
                <Camera className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input id="camera-name" type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Ex: Câmera da Garagem" required className="w-full pl-10 pr-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
            </div>
            <div>
              <label htmlFor="rtsp-url" className="block text-sm font-medium text-gray-700 mb-1">URL RTSP</label>
              <div className="relative">
                <Link className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input id="rtsp-url" type="url" value={rtspUrl} onChange={(e) => setRtspUrl(e.target.value)} placeholder="rtsp://exemplo.com/stream1" required className="w-full pl-10 pr-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="latitude" className="block text-sm font-medium text-gray-700 mb-1">Latitude (Opcional)</label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input id="latitude" type="number" step="any" value={latitude} onChange={(e) => setLatitude(e.target.value)} placeholder="-23.5505" className="w-full pl-10 pr-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
                </div>
              </div>
              <div>
                <label htmlFor="longitude" className="block text-sm font-medium text-gray-700 mb-1">Longitude (Opcional)</label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input id="longitude" type="number" step="any" value={longitude} onChange={(e) => setLongitude(e.target.value)} placeholder="-46.6333" className="w-full pl-10 pr-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
                </div>
              </div>
            </div>
          </div>
          <div className="flex justify-end gap-3 mt-6">
            <button type="button" onClick={handleClose} className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md">Cancelar</button>
            <button type="submit" disabled={isSubmitting || !name.trim() || !rtspUrl.trim()} className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50">
              {isSubmitting ? 'Adicionando...' : 'Adicionar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default AddCameraModal