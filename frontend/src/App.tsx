import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import ResumeForm from './components/ResumeForm';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import Dashboard from './components/Dashboard';
import { motion } from 'framer-motion';
import { Sparkles, Shield, Zap } from 'lucide-react';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
}

function Home() {
  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6">
      <div className="relative pt-10 pb-20 md:pt-16 md:pb-32 overflow-hidden">
        {/* Decorative Background Elements */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[500px] bg-gradient-to-b from-primary/5 to-transparent -z-10 blur-3xl opacity-50 rounded-full" />
        
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16 relative"
        >
          <motion.div 
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", damping: 12 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-xs font-black uppercase tracking-widest mb-8 shadow-sm border border-primary/10"
          >
            <Sparkles className="w-3.5 h-3.5" />
            Next-Gen Career Intelligence
          </motion.div>
          
          <h1 className="text-6xl md:text-8xl font-black tracking-tighter text-foreground mb-6 leading-[0.9]">
            Optimize<span className="text-primary">.</span><br />
            Apply<span className="text-primary">.</span><br />
            Succeed<span className="text-primary">.</span>
          </h1>
          
          <p className="max-w-2xl mx-auto text-xl text-muted-foreground font-medium mb-10 leading-relaxed">
            Mployable uses advanced AI to bridge the gap between your technical profile and your dream job. Tailored resumes that bypass ATS and impress recruiters.
          </p>

          <div className="flex flex-wrap justify-center gap-12 mt-16 opacity-50">
            <div className="flex items-center gap-2">
                <Shield className="w-5 h-5" />
                <span className="text-sm font-bold uppercase tracking-tighter">ATS Optimized</span>
            </div>
            <div className="flex items-center gap-2">
                <Zap className="w-5 h-5" />
                <span className="text-sm font-bold uppercase tracking-tighter">Instant Generation</span>
            </div>
            <div className="flex items-center gap-2 text-primary opacity-100">
                <Sparkles className="w-5 h-5" />
                <span className="text-sm font-black uppercase tracking-tighter">Gemini 2.0 Powered</span>
            </div>
          </div>
        </motion.div>
      </div>

      <div className="relative">
        <div className="absolute inset-0 bg-primary/5 -skew-y-3 -z-10 rounded-[4rem]" />
        <div className="py-20">
            <ResumeForm />
        </div>
      </div>
      
      <footer className="mt-32 pb-12 text-center">
        <p className="text-sm font-black text-muted-foreground uppercase tracking-[0.2em] flex items-center justify-center gap-4">
          <span className="w-8 h-[1px] bg-border" />
          The Future of Engineering Applications
          <span className="w-8 h-[1px] bg-border" />
        </p>
      </footer>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-background text-foreground selection:bg-primary/20 selection:text-primary transition-colors">
          <Navbar />
          <main className="relative">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<LoginForm />} />
              <Route path="/register" element={<RegisterForm />} />
              <Route 
                path="/dashboard" 
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                } 
              />
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;

