import React, { useEffect } from 'react';
import { Search } from 'lucide-react';
import { useSightingStore } from '../stores/sightingStore';
import AppLayout from '../components/AppLayout';
import FilterSidebar from '../components/FilterSidebar';
import SightingCard from '../components/SightingCard';

const DetectionsPage: React.FC = () => {
  const { sightings, isLoading, fetchSightings } = useSightingStore();

  useEffect(() => {
    fetchSightings();
  }, [fetchSightings]);

  return (
    <AppLayout>
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 flex items-center">
          <Search className="w-7 h-7 mr-3" />
          Detecções de Veículos
        </h2>
        <p className="text-gray-600 mt-1">Filtre e visualize os avistamentos registados pelo sistema.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Coluna de Filtros */}
        <div className="lg:col-span-1">
          <FilterSidebar />
        </div>

        {/* Coluna de Resultados */}
        <div className="lg:col-span-3">
          {isLoading ? (
            <div className="p-8 text-center bg-white rounded-lg shadow-sm">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">A carregar detecções...</p>
            </div>
          ) : sightings.length === 0 ? (
            <div className="p-8 text-center bg-white rounded-lg shadow-sm">
              <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Nenhuma detecção encontrada</h3>
              <p className="text-gray-600">Tente ajustar os seus filtros ou aguarde novos avistamentos.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {sightings.map((sighting) => (
                <SightingCard key={sighting.id} sighting={sighting} />
              ))}
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
};

export default DetectionsPage;