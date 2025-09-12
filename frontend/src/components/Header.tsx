import React from 'react';
import { LogOut, User, Settings } from 'lucide-react';
import { useAuthStore } from '../stores/authStore';
import { Link } from 'react-router-dom';

const Header: React.FC = () => {
  const { user, logout } = useAuthStore();
  const handleLogout = () => { logout(); };

  return (
    <header className="bg-white shadow-sm border-b sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-end items-center h-16">
          <div className="flex items-center space-x-4">
            <div className="flex items-center text-sm text-gray-700">
              <User className="w-4 h-4 mr-2" />
              {/* Se o backend tivesse nome/apelido, usariamos aqui. Por enquanto, email. */}
              <span>{user?.email}</span>
            </div>
            <Link to="/settings" className="text-gray-500 hover:text-blue-600 transition-colors" title="Configurações">
              <Settings className="w-5 h-5" />
            </Link>
            <button onClick={handleLogout} className="flex items-center text-sm text-gray-700 hover:text-red-600 transition-colors" title="Sair">
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;