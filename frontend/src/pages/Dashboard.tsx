
import React, { useState, useEffect } from 'react';
import {Eye, Camera, Car, TrendingUp} from 'lucide-react';
import api from '../config/api';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface DashboardStats {
  sightingsToday: number;
  activeCameras: number;
  uniqueVehiclesMonth: number;
}

interface SightingsChart {
  date: string;
  count: number;
}

interface Sighting {
  id: number;
  license_plate: string;
  timestamp: string;
  camera_id: number;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    sightingsToday: 0,
    activeCameras: 0,
    uniqueVehiclesMonth: 0,
  });
  const [chartData, setChartData] = useState<SightingsChart[]>([]);
  const [recentSightings, setRecentSightings] = useState<Sighting[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      
      // Carregar estatísticas
      const [sightingsTodayRes, activeCamerasRes, uniqueVehiclesRes] = await Promise.all([
        api.get('/dashboard/sightings-today'),
        api.get('/dashboard/active-cameras'),
        api.get('/dashboard/unique-vehicles-month'),
      ]);

      setStats({
        sightingsToday: sightingsTodayRes.data,
        activeCameras: activeCamerasRes.data,
        uniqueVehiclesMonth: uniqueVehiclesRes.data,
      });

      // Carregar dados do gráfico
      const chartRes = await api.get('/dashboard/sightings-last-7-days');
      setChartData(chartRes.data);

      // Carregar últimos avistamentos
      const sightingsRes = await api.get('/sightings/?limit=5&skip=0');
      setRecentSightings(sightingsRes.data);
    } catch (error) {
      console.error('Erro ao carregar dados do dashboard:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Avistamentos nos Últimos 7 Dias',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  const chartDataConfig = {
    labels: chartData.map(item => new Date(item.date).toLocaleDateString('pt-BR')),
    datasets: [
      {
        label: 'Avistamentos',
        data: chartData.map(item => item.count),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
      },
    ],
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('pt-BR');
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">Visão geral do sistema GT-Vision</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Eye className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Avistamentos Hoje</p>
              <p className="text-2xl font-bold text-gray-900">{stats.sightingsToday}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Camera className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Câmeras Ativas</p>
              <p className="text-2xl font-bold text-gray-900">{stats.activeCameras}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Car className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Veículos Únicos no Mês</p>
              <p className="text-2xl font-bold text-gray-900">{stats.uniqueVehiclesMonth}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center mb-6">
          <TrendingUp className="h-6 w-6 text-blue-600 mr-2" />
          <h2 className="text-xl font-semibold text-gray-900">Tendência de Avistamentos</h2>
        </div>
        {chartData.length > 0 ? (
          <Line options={chartOptions} data={chartDataConfig} />
        ) : (
          <p className="text-gray-500 text-center py-8">Nenhum dado disponível para o gráfico</p>
        )}
      </div>

      {/* Recent Sightings */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Últimos Avistamentos</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Placa
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Data/Hora
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Câmera ID
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {recentSightings.length > 0 ? (
                recentSightings.map((sighting) => (
                  <tr key={sighting.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {sighting.license_plate}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatTimestamp(sighting.timestamp)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {sighting.camera_id}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={3} className="px-6 py-4 text-center text-sm text-gray-500">
                    Nenhum avistamento encontrado
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
