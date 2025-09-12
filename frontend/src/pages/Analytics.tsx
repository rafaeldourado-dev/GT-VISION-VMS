import React from 'react';
import AppLayout from '../components/AppLayout';
import { BarChart2, Cpu, HardDrive, AlertTriangle } from 'lucide-react';
import MetricCard from '../components/MetricCard'; // Importar o novo componente

// Placeholder para a lista de eventos
const EventsListPlaceholder: React.FC = () => (
    <div className="bg-white p-6 rounded-lg shadow-sm col-span-1 md:col-span-3">
        <h3 className="text-lg font-semibold text-gray-800 flex items-center mb-4">
            <AlertTriangle className="w-5 h-5 mr-2 text-yellow-500" />
            Eventos Recentes
        </h3>
        <div className="h-96 flex items-center justify-center bg-gray-100 rounded-md">
            <p className="text-gray-500 italic">Funcionalidade de eventos em desenvolvimento</p>
        </div>
    </div>
);

const Analytics: React.FC = () => {
    // Dados estáticos como exemplo
    const systemMetrics = {
        cpuUsage: 45,
        gpuUsage: 'N/A',
        memoryUsage: 8.2,
        totalMemory: 16
    };

    return (
        <AppLayout>
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-gray-900 flex items-center">
                    <BarChart2 className="w-7 h-7 mr-3" /> Analíticos e Eventos
                </h2>
                <p className="text-gray-600 mt-1">Acompanhe as detecções e o status do sistema.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <MetricCard
                    title="Uso de CPU"
                    value={`${systemMetrics.cpuUsage}%`}
                    icon={Cpu}
                    color="blue"
                    delay={0.1}
                />
                
                <MetricCard
                    title="Uso de GPU"
                    value={`${systemMetrics.gpuUsage}`}
                    icon={Cpu}
                    color="purple"
                    delay={0.2}
                />
                
                <MetricCard
                    title="Uso de Memória"
                    value={`${systemMetrics.memoryUsage} GB`}
                    subtitle={`de ${systemMetrics.totalMemory} GB`}
                    icon={HardDrive}
                    color="green"
                    delay={0.3}
                />
                
                <EventsListPlaceholder />
            </div>
        </AppLayout>
    );
};

export default Analytics;