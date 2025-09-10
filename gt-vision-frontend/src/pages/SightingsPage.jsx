
import React, { useState, useEffect } from 'react'
import { sightingsService } from '../services/api'
import toast from 'react-hot-toast'

const SightingsPage = () => {
  const [sightings, setSightings] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchSightings = async () => {
      try {
        setLoading(true)
        const data = await sightingsService.getAll()
        setSightings(data)
      } catch (error) {
        toast.error('Erro ao carregar avistamentos')
        console.error('Erro ao buscar avistamentos:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchSightings()
  }, [])

  const formatDateTime = (dateString) => {
    if (!dateString) return 'N/A'
    try {
      return new Date(dateString).toLocaleString('pt-BR')
    } catch {
      return 'Data inválida'
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Avistamentos</h1>
        <p className="mt-1 text-sm text-gray-500">
          Histórico de veículos detectados pelas câmeras
        </p>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Data/Hora
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Câmera
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Placa
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Tipo de Veículo
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Confiança
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
            ) : sightings.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-4 text-center text-gray-500">
                  Nenhum avistamento registrado.
                </td>
              </tr>
            ) : (
              sightings.map((sighting) => (
                <tr key={sighting.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatDateTime(sighting.timestamp)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {sighting.camera_name || `Câmera ${sighting.camera_id}`}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {sighting.license_plate || 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {sighting.vehicle_type || 'Não identificado'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {sighting.confidence ? `${(sighting.confidence * 100).toFixed(1)}%` : 'N/A'}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default SightingsPage
