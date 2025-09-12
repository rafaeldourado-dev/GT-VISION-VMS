import React from 'react';
import { NavLink, Link } from 'react-router-dom';
import { LayoutDashboard, Map, Settings, BarChart3 } from 'lucide-react'; // Adicionado ícone do Mapa
import { motion } from 'framer-motion';

const Sidebar: React.FC = () => {
  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    // { name: 'Mapa', href: '/mapa', icon: Map }, // NOVO: Link para a página do mapa
    { name: 'Analíticos', href: '/analytics', icon: BarChart3 },
  ];

  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
      isActive
        ? 'bg-blue-100 text-blue-700'
        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
    }`;

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex-col hidden lg:flex">
      <div className="h-16 flex items-center justify-center border-b px-4">
        <Link to="/dashboard" className="flex items-center space-x-3">
          <img src="/logo.png" alt="GT Vision Logo" className="h-9 w-9 rounded-full" />
          <h1 className="text-xl font-bold text-gray-900">GT Vision</h1>
        </Link>
      </div>
      <nav className="flex-1 p-4 space-y-2">
        {navigation.map((item, index) => (
            <motion.li key={item.name} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.1 }} className="list-none">
                <NavLink to={item.href} className={navLinkClass}>
                    <item.icon className="w-5 h-5 mr-3" />
                    {item.name}
                </NavLink>
            </motion.li>
        ))}
      </nav>
      <div className="p-4 border-t">
        <NavLink to="/settings" className={navLinkClass}>
          <Settings className="w-5 h-5 mr-3" />
          Configurações
        </NavLink>
      </div>
    </aside>
  );
};

export default Sidebar;