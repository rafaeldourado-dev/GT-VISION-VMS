import React, { useState, useEffect } from 'react';
import { useUserStore } from '../stores/userStore';
import { X, User, Save } from 'lucide-react';

interface UserData {
  id?: number;
  full_name: string;
  email: string;
  role: string;
  is_active: boolean;
  password?: string;
}

interface UserModalProps {
  isOpen: boolean;
  onClose: () => void;
  userToEdit?: UserData | null;
}

const UserModal: React.FC<UserModalProps> = ({ isOpen, onClose, userToEdit }) => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('CLIENT_USER');
  const [isActive, setIsActive] = useState(true);
  const { addUser, updateUser } = useUserStore();

  const isEditMode = !!userToEdit;

  useEffect(() => {
    if (userToEdit) {
      setFullName(userToEdit.full_name);
      setEmail(userToEdit.email);
      setRole(userToEdit.role);
      setIsActive(userToEdit.is_active);
      setPassword(''); // Senha não é preenchida na edição
    } else {
      setFullName('');
      setEmail('');
      setPassword('');
      setRole('CLIENT_USER');
      setIsActive(true);
    }
  }, [userToEdit, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const userData: any = {
      full_name: fullName,
      email,
      role,
      is_active: isActive,
    };

    if (password || !isEditMode) {
      userData.password = password;
    }

    const success = isEditMode
      ? await updateUser(userToEdit.id!, userData)
      : await addUser(userData);

    if (success) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-800 flex items-center">
            <User className="w-6 h-6 mr-2" />
            {isEditMode ? 'Editar Usuário' : 'Adicionar Novo Usuário'}
          </h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-800"><X className="w-6 h-6" /></button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Nome Completo</label>
            <input type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} required className="mt-1 block w-full input" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className="mt-1 block w-full input" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Senha</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required={!isEditMode} placeholder={isEditMode ? 'Deixe em branco para não alterar' : ''} className="mt-1 block w-full input" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Perfil (Role)</label>
            <select value={role} onChange={(e) => setRole(e.target.value)} className="mt-1 block w-full input">
              <option value="CLIENT_USER">Usuário</option>
              <option value="CLIENT_ADMIN">Admin do Cliente</option>
            </select>
          </div>
          <div className="flex items-center">
            <input type="checkbox" id="is_active" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
            <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">Usuário Ativo</label>
          </div>
          <div className="flex justify-end space-x-3 pt-4">
            <button type="button" onClick={onClose} className="btn-secondary">Cancelar</button>
            <button type="submit" className="btn-primary flex items-center"><Save className="w-5 h-5 mr-2" /> Salvar</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UserModal;