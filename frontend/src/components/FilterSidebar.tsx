import React, { useState, useEffect } from 'react';
import { Filter, Search, X } from 'lucide-react';
import { useSightingStore } from '../stores/sightingStore';
import { useCameraStore } from '../stores/cameraStore';

const FilterSidebar: React.FC = () => {
  const { filters, setFilters, fetchSightings } = useSightingStore();
  const { cameras, fetchCameras } = useCameraStore();

  const [plate, setPlate] = useState(filters.license_plate || '');
  const [cameraId, setCameraId] = useState(filters.camera_id || '');
  const [startDate, setStartDate] = useState(filters.start_date || '');
  const [endDate, setEndDate] = useState(filters.end_date || '');

  useEffect(() => {
    // Carrega as câmeras para preencher o seletor
    fetchCameras();
  }, [fetchCameras]);

  const handleFilter = () => {
    setFilters({ license_plate: plate, camera_id: cameraId, start_date: startDate, end_date: endDate });
    fetchSightings();
  };

  const handleClear = () => {
    setPlate('');
    setCameraId('');
    setStartDate('');
    setEndDate('');
    setFilters({ license_plate: '', camera_id: '', start_date: '', end_date: '' });
    fetchSightings();
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <h3 className="text-lg font-semibold text-gray-800 flex items-center mb-4">
        <Filter className="w-5 h-5 mr-2" />
        Filtros
      </h3>
      <div className="space-y-4">
        <div>
          <label htmlFor="plate-search" className="block text-sm font-medium text-gray-700 mb-1">
            Pesquisar Placa
          </label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              id="plate-search"
              type="text"
              value={plate}
              onChange={(e) => setPlate(e.target.value.toUpperCase())}
              placeholder="ABC-1234"
              className="w-full pl-10 pr-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        <div>
          <label htmlFor="camera-select" className="block text-sm font-medium text-gray-700 mb-1">
            Câmera
          </label>
          <select
            id="camera-select"
            value={cameraId}
            onChange={(e) => setCameraId(e.target.value)}
            className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todas as câmeras</option>
            {cameras.map((camera) => (
              <option key={camera.id} value={camera.id}>{camera.name}</option>
            ))}
          </select>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="start-date" className="block text-sm font-medium text-gray-700 mb-1">
              De
            </label>
            <input type="date" id="start-date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label htmlFor="end-date" className="block text-sm font-medium text-gray-700 mb-1">
              Até
            </label>
            <input type="date" id="end-date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
        </div>
      </div>
      <div className="flex flex-col gap-3 mt-6">
        <button
          onClick={handleFilter}
          className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-all shadow-sm"
        >
          <Search className="w-4 h-4 mr-2" />
          Aplicar Filtro
        </button>
        <button
          onClick={handleClear}
          className="w-full flex items-center justify-center px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-all"
        >
          <X className="w-4 h-4 mr-2" />
          Limpar
        </button>
      </div>
    </div>
  );
};

export default FilterSidebar;