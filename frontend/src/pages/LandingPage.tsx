import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Video, Cpu, ShieldCheck, ArrowRight, Send } from 'lucide-react';
import { motion } from 'framer-motion';

// Componente para o Card de Funcionalidade
const FeatureCard = ({ icon: Icon, title, children, delay }: any) => (
  <motion.div
    initial={{ opacity: 0, y: 30 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ delay, duration: 0.5 }}
    className="bg-slate-800/50 p-6 rounded-lg border border-slate-700 backdrop-blur-sm transition-all duration-300 hover:border-cyan-400/50 hover:bg-slate-800/80 hover:-translate-y-2"
  >
    <div className="flex items-center gap-4">
      <div className="bg-slate-900 p-3 rounded-md border border-slate-700">
        <Icon className="w-6 h-6 text-cyan-400" />
      </div>
      <h3 className="text-xl font-semibold text-white">{title}</h3>
    </div>
    <p className="mt-4 text-slate-400">{children}</p>
  </motion.div>
);

const LandingPage: React.FC = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  
  // Estados para o formulário de contato
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Lógica para enviar o formulário.
    // Por enquanto, apenas exibimos no console.
    // Você precisará integrar com um serviço de email ou seu backend aqui.
    console.log({ name, email, message });
    alert('Mensagem enviada com sucesso! (Verifique o console)');
    // Limpa o formulário
    setName('');
    setEmail('');
    setMessage('');
  };


  useEffect(() => {
    const handleMouseMove = (event: MouseEvent) => {
      setMousePosition({ x: event.clientX, y: event.clientY });
    };

    window.addEventListener('mousemove', handleMouseMove);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-300 font-sans overflow-x-hidden">
      
      <div 
        className="pointer-events-none fixed inset-0 z-30 transition duration-300"
        style={{
          background: `radial-gradient(600px at ${mousePosition.x}px ${mousePosition.y}px, rgba(22, 163, 224, 0.15), transparent 80%)`
        }}
      />
      
      <div className="relative z-10">
        
        <header className="fixed top-0 left-0 right-0 bg-slate-900/80 backdrop-blur-md z-50 border-b border-slate-800">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <Link to="/" className="flex items-center">
                <img src="/logo.png" alt="GT Vision Logo" className="h-9 w-9 mr-3 rounded-full" />
                <h1 className="text-2xl font-bold text-white">GT Vision</h1>
              </Link>
              <Link to="/login" className="flex items-center px-4 py-2 text-sm font-medium text-white bg-cyan-500 rounded-md hover:bg-cyan-600 transition-colors shadow-[0_0_15px_rgba(56,189,248,0.3)]">
                <span>Acessar Plataforma</span>
                <ArrowRight className="w-4 h-4 ml-2" />
              </Link>
            </div>
          </div>
        </header>

        <main>
          <section className="relative min-h-screen flex items-center pt-16">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
              <div className="grid lg:grid-cols-2 gap-12 items-center">
                <div className="text-center lg:text-left">
                  <motion.h2 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2, duration: 0.5 }} className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-white leading-tight">
                    Monitoramento Inteligente, <span className="text-cyan-400">Simplificado.</span>
                  </motion.h2>
                  <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4, duration: 0.5 }} className="mt-4 text-lg text-slate-400 max-w-xl mx-auto lg:mx-0">
                    A GT Vision transforma suas câmeras em um sistema proativo de vigilância com o poder da Inteligência Artificial.
                  </motion.p>
                  <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6, duration: 0.5 }}>
                    <Link to="/login" className="mt-8 inline-block px-8 py-3 text-lg font-semibold text-white bg-cyan-500 rounded-lg hover:bg-cyan-600 transition-transform transform hover:scale-105 shadow-[0_0_20px_rgba(56,189,248,0.4)]">
                      Comece a Monitorar
                    </Link>
                  </motion.div>
                </div>
                <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.4, duration: 0.8 }} className="mt-12 lg:mt-0">
                  <img 
                    src="https://images.unsplash.com/photo-1526628953301-3e589a6a8b74?q=80&w=1920&auto=format&fit=crop" 
                    alt="Painel de Monitoramento" 
                    className="rounded-lg shadow-2xl shadow-cyan-500/10 border border-slate-700"
                  />
                </motion.div>
              </div>
            </div>
          </section>

          <section className="py-20 sm:py-24">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="text-center mb-16">
                <h3 className="text-3xl lg:text-4xl font-bold text-white">Inteligência com Agilidade e Precisão</h3>
                <p className="mt-3 text-slate-400 max-w-2xl mx-auto">Nossa plataforma integra e potencializa as ferramentas que você já usa, entregando mais eficiência e resultados.</p>
              </div>
              <div className="grid md:grid-cols-3 gap-8">
                <FeatureCard icon={Video} title="Streaming em Tempo Real" delay={0.1}>
                  Visualize todas as suas câmeras em um único dashboard, de qualquer lugar, com baixa latência.
                </FeatureCard>
                <FeatureCard icon={Cpu} title="Detecção com IA" delay={0.2}>
                  Receba alertas com a detecção automática de pessoas, veículos e comportamentos suspeitos.
                </FeatureCard>
                <FeatureCard icon={ShieldCheck} title="Seguro e Centralizado" delay={0.3}>
                  Gerencie tudo em uma plataforma segura, criptografada e unificada na nuvem.
                </FeatureCard>
              </div>
            </div>
          </section>
          
          {/* ========== FINAL CTA COM FORMULÁRIO ========== */}
          <section className="text-center py-20 sm:py-24">
            <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
              <h2 className="text-3xl sm:text-4xl font-extrabold text-white">Pronto para elevar sua operação?</h2>
              <p className="mt-4 text-lg text-slate-400">Descubra como podemos simplificar processos e maximizar resultados na sua operação.</p>
              
              <motion.form 
                onSubmit={handleFormSubmit}
                initial={{ opacity: 0, y: 20 }} 
                whileInView={{ opacity: 1, y: 0 }} 
                viewport={{ once: true }} 
                transition={{ delay: 0.2 }}
                className="mt-8 space-y-4 text-left"
              >
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="name" className="sr-only">Nome</label>
                    <input type="text" id="name" value={name} onChange={e => setName(e.target.value)} placeholder="Seu nome" required className="w-full bg-slate-800/80 border border-slate-700 rounded-md py-3 px-4 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500" />
                  </div>
                  <div>
                    <label htmlFor="email" className="sr-only">Email</label>
                    <input type="email" id="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="Seu email" required className="w-full bg-slate-800/80 border border-slate-700 rounded-md py-3 px-4 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500" />
                  </div>
                </div>
                <div>
                  <label htmlFor="message" className="sr-only">Mensagem</label>
                  <textarea id="message" value={message} onChange={e => setMessage(e.target.value)} placeholder="Como podemos ajudar?" rows={4} required className="w-full bg-slate-800/80 border border-slate-700 rounded-md py-3 px-4 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500"></textarea>
                </div>
                <div className="text-center">
                  <button type="submit" className="inline-flex items-center justify-center px-8 py-3 text-lg font-semibold text-white bg-cyan-500 rounded-lg hover:bg-cyan-600 transition-transform transform hover:scale-105 shadow-[0_0_20px_rgba(56,189,248,0.4)]">
                    <Send className="w-5 h-5 mr-3" />
                    Enviar Mensagem
                  </button>
                </div>
              </motion.form>

            </div>
          </section>
        </main>

        <footer className="bg-slate-900/50 border-t border-slate-800">
          <div className="max-w-7xl mx-auto py-6 px-4 text-center text-slate-500">
            <p>&copy; 2025 GT Vision. Todos os direitos reservados.</p>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default LandingPage;