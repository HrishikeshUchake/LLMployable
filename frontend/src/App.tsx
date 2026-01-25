import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import ResumeForm from './components/ResumeForm';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import Dashboard from './components/Dashboard';
import { motion } from 'framer-motion';
import { Rocket } from 'lucide-react';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
}

function Home() {
  return (
    <div className="max-w-4xl mx-auto">
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-16"
      >
        <motion.div 
          whileHover={{ rotate: 15, scale: 1.1 }}
          className="inline-flex items-center justify-center p-4 bg-indigo-600 rounded-3xl shadow-xl shadow-indigo-200 mb-6 cursor-pointer"
        >
          <Rocket className="w-10 h-10 text-white" />
        </motion.div>
        <h1 className="text-5xl font-black tracking-tight text-slate-900 sm:text-6xl mb-4">
          Mployable<span className="text-indigo-600">.</span>
        </h1>
        <p className="max-w-xl mx-auto text-xl text-slate-500 font-medium">
          AI-powered resume tailoring that actually works. Leverage your GitHub & LinkedIn to match any job description.
        </p>
      </motion.div>
      
      <ResumeForm />
      
      <p className="mt-16 text-center text-sm font-bold text-slate-400 uppercase tracking-widest flex items-center justify-center gap-2">
        Powered by <span className="text-slate-600">Google Gemini</span> &bull; Built for <span className="text-indigo-600">The Future of Work</span>
      </p>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-[#fafafa] text-slate-900 selection:bg-indigo-100 selection:text-indigo-700">
          <Navbar />
          <main className="py-12 px-4 sm:px-6 lg:px-8">
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

