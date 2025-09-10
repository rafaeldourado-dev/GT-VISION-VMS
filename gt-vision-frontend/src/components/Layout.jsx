
import React from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import {LayoutDashboard, Camera, Eye, Ticket, LogOut, Menu, X} from 'lucide-react'
import { useState } from 'react'
import toast from 'react-hot-toast'

const Layout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const navigate = useNavigate()

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Câmeras', href: '/cameras', icon: Camera },
    { name: 'Avistamentos', href: '/sightings', icon: Eye },
    { name: 'Tickets', href: '/tickets', icon: Ticket },
  ]

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    toast.success('Logout realizado com sucesso!')
    navigate('/login')
  }

  return (
    <div className="h-screen flex overflow-hidden bg-gray-100">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'block' : 'hidden'} fixed inset-0 flex z-40 md:hidden`}>
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)} />
        <div className="relative flex-1 flex flex-col max-w-xs w-full bg-gray-900">
          <div className="absolute top-0 right-0 -mr-12 pt-2">
            <button
              className="ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="h-6 w-6 text-white" />
            </button>
          </div>
          <SidebarContent navigation={navigation} onLogout={handleLogout} />
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden md:flex md:flex-shrink-0">
        <div className="flex flex-col w-64">
          <div className="flex flex-col h-0 flex-1 bg-gray-900">
            <SidebarContent navigation={navigation} onLogout={handleLogout} />
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex flex-col w-0 flex-1 overflow-hidden">
        <div className="md:hidden pl-1 pt-1 sm:pl-3 sm:pt-3">
          <button
            className="-ml-0.5 -mt-0.5 h-12 w-12 inline-flex items-center justify-center rounded-md text-gray-500 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-6 w-6" />
          </button>
        </div>
        
        <main className="flex-1 relative overflow-y-auto focus:outline-none bg-gray-50">
          <div className="py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
              <Outlet />
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

const SidebarContent = ({ navigation, onLogout }) => (
  <>
    <div className="flex items-center h-16 flex-shrink-0 px-4 bg-gray-900">
      <div className="flex items-center">
        <div className="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center">
          <Camera className="h-5 w-5 text-white" />
        </div>
        <span className="ml-3 text-white text-lg font-semibold">GT-Vision</span>
      </div>
    </div>
    
    <div className="flex-1 flex flex-col">
      <nav className="flex-1 px-2 py-4 bg-gray-900 space-y-1">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              `${
                isActive
                  ? 'bg-gray-700 text-white'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'
              } group flex items-center px-2 py-2 text-sm font-medium rounded-md`
            }
          >
            <item.icon className="mr-3 h-5 w-5" />
            {item.name}
          </NavLink>
        ))}
      </nav>
      
      <div className="flex-shrink-0 flex bg-gray-900 p-4">
        <button
          onClick={onLogout}
          className="flex-shrink-0 w-full group block text-gray-300 hover:text-white hover:bg-gray-700 rounded-md px-2 py-2 text-sm font-medium"
        >
          <div className="flex items-center">
            <LogOut className="mr-3 h-5 w-5" />
            <span>Sair</span>
          </div>
        </button>
      </div>
    </div>
  </>
)

export default Layout
