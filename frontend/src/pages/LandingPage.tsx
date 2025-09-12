import React from 'react';
import { Link } from 'react-router-dom';
import { Video, Cpu, ShieldCheck, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-white text-gray-800">
      <header className="fixed top-0 left-0 right-0 bg-white bg-opacity-80 backdrop-blur-md z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <img src="/logo.png" alt="GT Vision Logo" className="h-9 w-9 mr-3 rounded-full" />
              <h1 className="text-2xl font-bold text-gray-900">GT Vision</h1>
            </div>
            <Link to="/login" className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors">
              <span>Acessar Plataforma</span>
              <ArrowRight className="w-4 h-4 ml-2" />
            </Link>
          </div>
        </div>
      </header>

      <main className="pt-24 pb-12">
        <section className="text-center max-w-4xl mx-auto px-4">
          <motion.h2 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="text-4xl md:text-5xl font-extrabold text-gray-900">
            Monitoramento Inteligente, Simplificado.
          </motion.h2>
          <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="mt-4 text-lg text-gray-600">
            A GT Vision transforma suas câmeras em um sistema proativo de vigilância com o poder da Inteligência Artificial.
          </motion.p>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
            <Link to="/login" className="mt-8 inline-block px-8 py-3 text-lg font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-transform transform hover:scale-105">
              Comece a Monitorar
            </Link>
          </motion.div>
        </section>

        <section className="max-w-7xl mx-auto mt-20 px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-3 gap-8">
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.1 }} className="text-center p-6 bg-gray-50 rounded-lg">
              <Video className="w-12 h-12 mx-auto text-blue-600 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Streaming em Tempo Real</h3>
              <p className="text-gray-600">Visualize todas as suas câmeras em um único dashboard, de qualquer lugar.</p>
            </motion.div>
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.2 }} className="text-center p-6 bg-gray-50 rounded-lg">
              <Cpu className="w-12 h-12 mx-auto text-blue-600 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Detecção com IA</h3>
              <p className="text-gray-600">Receba alertas com a detecção automática de pessoas e carros.</p>
            </motion.div>
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.3 }} className="text-center p-6 bg-gray-50 rounded-lg">
              <ShieldCheck className="w-12 h-12 mx-auto text-blue-600 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Seguro e Centralizado</h3>
              <p className="text-gray-600">Gerencie tudo em uma plataforma segura e unificada.</p>
            </motion.div>
          </div>
        </section>
      </main>

      <footer className="bg-gray-100 mt-12">
        <div className="max-w-7xl mx-auto py-6 px-4 text-center text-gray-500">
          <p>&copy; 2025 GT Vision. Todos os direitos reservados.</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;