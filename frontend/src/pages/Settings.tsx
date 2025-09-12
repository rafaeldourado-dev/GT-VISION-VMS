import React, { useState } from 'react';
import { User, Palette, KeyRound } from 'lucide-react';
import AppLayout from '../components/AppLayout';

// Card para editar perfil
const ProfileCard: React.FC = () => {
    // No futuro, os valores virão do `useAuthStore`
    const [name, setName] = useState(''); 
    const [nickname, setNickname] = useState('');

    return (
        <div className="bg-white p-6 rounded-lg shadow-sm">
            <h3 className="text-lg font-semibold text-gray-800 flex items-center mb-4">
                <User className="w-5 h-5 mr-2" />
                Perfil do Usuário
            </h3>
            <form className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-600">Nome</label>
                    <input type="text" value={name} onChange={e => setName(e.target.value)} placeholder="Seu nome completo" className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 cursor-not-allowed" disabled />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-600">Apelido</label>
                    <input type="text" value={nickname} onChange={e => setNickname(e.target.value)} placeholder="Como você quer ser chamado" className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 cursor-not-allowed" disabled />
                </div>
                <div className="flex justify-end pt-2">
                    <button type="submit" className="px-5 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed" disabled>
                        Salvar Perfil
                    </button>
                </div>
                 <p className="text-xs text-gray-500 text-right italic">Funcionalidade a ser implementada no backend.</p>
            </form>
        </div>
    );
};

// Card para preferências de aparência
const AppearanceCard: React.FC = () => {
    const [theme, setTheme] = useState('light'); // 'light' ou 'dark'

    return (
        <div className="bg-white p-6 rounded-lg shadow-sm">
            <h3 className="text-lg font-semibold text-gray-800 flex items-center mb-4">
                <Palette className="w-5 h-5 mr-2" />
                Aparência
            </h3>
            <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-600">Tema</label>
                <select value={theme} onChange={e => setTheme(e.target.value)} className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 cursor-not-allowed" disabled>
                    <option value="light">Claro (Padrão)</option>
                    <option value="dark">Escuro</option>
                </select>
                 <p className="text-xs text-gray-500 pt-2 italic">A funcionalidade de tema será implementada futuramente.</p>
            </div>
        </div>
    );
};


const Settings: React.FC = () => {
  return (
    <AppLayout>
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900">Configurações da Conta</h2>
        <p className="text-gray-600 mt-1">Gerencie suas informações e preferências da plataforma.</p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-8">
            <ProfileCard />
            <AppearanceCard />
        </div>
      </div>
    </AppLayout>
  );
};

export default Settings;