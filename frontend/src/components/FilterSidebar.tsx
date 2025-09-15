import React, { useState } from 'react';
import { Filter, Search, X } from 'lucide-react';
import { useSightingStore } from '../stores/sightingStore';

const FilterSidebar: React.FC = () => {
  const { filters, setFilters, fetchSightings } = useSightingStore();
  const [plate, setPlate] = useState(filters.license_plate || '');

  const handleFilter = () => {
    setFilters({ license_plate: plate });
    fetchSightings();
  };

  const handleClear = () => {
    setPlate('');
    setFilters({ license_plate: '' });
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