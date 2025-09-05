import { useState, useEffect } from "react";
import Sidebar from "../components/layout/Sidebar";
import Header from "../components/layout/Header";
import KpiCard from "../components/dashboard/KpiCard";
import RecentSightings from "../components/dashboard/RecentSightings";
import { Camera, Car, AlertTriangle } from "lucide-react";
import apiClient from "../api/apiClient";

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get("/dashboard/stats");
        setStats(response.data);
      } catch (error) {
        console.error("Erro ao buscar estatísticas do dashboard:", error);
        setStats({ online_cameras: 0, total_cameras: 0, sightings_today: 0, alerts_24h: 0 });
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return (
    <div className="flex min-h-screen w-full flex-col bg-muted/40">
      <Sidebar />
      <div className="flex flex-col sm:gap-4 sm:py-4 sm:pl-14">
        <Header />
        <main className="flex flex-1 flex-col gap-4 p-4 md:gap-8 md:p-8">
          {/* Grid para os cards de KPI */}
          <div className="grid gap-4 md:grid-cols-2 md:gap-8 lg:grid-cols-3">
            <KpiCard
              title="Câmeras Online"
              value={loading ? "..." : `${stats?.online_cameras} / ${stats?.total_cameras}`}
              description="Status de todas as câmeras"
              icon={Camera}
            />
            <KpiCard
              title="Avistamentos Hoje"
              value={loading ? "..." : stats?.sightings_today}
              description="+20.1% desde ontem"
              icon={Car}
            />
            <KpiCard
              title="Alertas (Últimas 24h)"
              value={loading ? "..." : stats?.alerts_24h}
              description="Veículos suspeitos detectados"
              icon={AlertTriangle}
            />
          </div>
          {/* Área para a tabela e futuro mapa */}
          <div className="grid gap-4 md:gap-8 lg:grid-cols-1">
            <RecentSightings />
          </div>
        </main>
      </div>
    </div>
  );
}