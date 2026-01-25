import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Briefcase, LogOut, LayoutDashboard, Menu, X, Mic } from 'lucide-react';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Navbar() {
  const { user, logout, isAuthenticated } = useAuth();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navLinks = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard, protected: true },
    { name: 'Mock Interview', path: '/mock-interview', icon: Mic, protected: true },
  ];

  return (
    <nav className="sticky top-0 z-40 w-full border-b border-white/10 glass">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center gap-2 group">
              <motion.div 
                whileHover={{ rotate: 12, scale: 1.1 }}
                className="bg-primary p-2 rounded-xl shadow-lg shadow-primary/20"
              >
                <Briefcase className="w-5 h-5 text-white" />
              </motion.div>
              <span className="text-2xl font-black tracking-tight text-foreground">
                LLMployable<span className="text-primary">.</span>
              </span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-10">
            {isAuthenticated && (
              <div className="flex items-center gap-2 bg-muted/50 p-1.5 rounded-2xl">
                {navLinks.map((link) => (
                  <Link
                    key={link.path}
                    to={link.path}
                    className={`flex items-center gap-2.5 px-5 py-2 rounded-xl text-sm font-black transition-smooth ${
                      location.pathname === link.path 
                        ? 'bg-card text-primary shadow-sm ring-1 ring-black/5' 
                        : 'text-muted-foreground hover:text-foreground hover:bg-card/50'
                    }`}
                  >
                    <link.icon className={`w-4 h-4 ${location.pathname === link.path ? 'text-primary' : 'text-muted-foreground'}`} />
                    {link.name}
                  </Link>
                ))}
              </div>
            )}

            <div className="flex items-center gap-4 ml-2">
              {isAuthenticated ? (
                <div className="flex items-center gap-8">
                  <div className="flex items-center gap-3 group">
                    <div className="flex flex-col items-end">
                      <span className="text-[10px] font-black text-muted-foreground uppercase tracking-[0.2em]">Verified</span>
                      <span className="text-sm font-black text-foreground group-hover:text-primary transition-colors">{user?.username}</span>
                    </div>
                    <div className="w-10 h-10 bg-gradient-to-br from-primary to-primary-dark rounded-xl flex items-center justify-center text-white font-black shadow-lg shadow-primary/20 ring-2 ring-white/10">
                        {user?.username?.[0]?.toUpperCase()}
                    </div>
                  </div>
                  <button
                    onClick={logout}
                    className="flex items-center gap-2 group text-sm font-black text-muted-foreground hover:text-danger hover:bg-danger/5 transition-smooth px-4 py-2.5 rounded-xl border border-transparent hover:border-danger/10"
                  >
                    <LogOut className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
                    Logout
                  </button>
                </div>
              ) : (
                <div className="flex items-center gap-4">
                  <Link 
                    to="/login" 
                    className="px-5 py-2.5 text-sm font-black text-muted-foreground hover:text-primary transition-smooth"
                  >
                    Login
                  </Link>
                  <Link 
                    to="/register" 
                    className="bg-foreground hover:bg-primary text-white px-7 py-3 rounded-2xl text-sm font-black shadow-xl shadow-primary/10 transition-smooth hover:-translate-y-1"
                  >
                    Get Started Free
                  </Link>
                </div>
              )}
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="p-2 text-muted-foreground hover:text-foreground transition-smooth"
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-card border-b border-white/10 overflow-hidden shadow-2xl"
          >
            <div className="px-4 pt-4 pb-8 space-y-4">
              {isAuthenticated ? (
                <>
                  <div className="flex items-center gap-4 px-4 py-6 bg-muted/50 rounded-[2rem] mb-6 shadow-inner ring-1 ring-white/5">
                    <div className="w-12 h-12 bg-gradient-to-br from-primary to-primary-dark rounded-2xl flex items-center justify-center text-white font-black shadow-lg shadow-primary/20">
                      {user?.username?.[0]?.toUpperCase()}
                    </div>
                    <div>
                      <p className="text-[10px] font-black text-muted-foreground uppercase tracking-[0.2em]">Active Member</p>
                      <p className="text-xl font-black text-foreground">{user?.username}</p>
                    </div>
                  </div>
                  {navLinks.map((link) => (
                    <Link
                      key={link.path}
                      to={link.path}
                      onClick={() => setIsMobileMenuOpen(false)}
                      className={`flex items-center gap-4 px-6 py-4 rounded-2xl text-base font-black transition-smooth ${
                        location.pathname === link.path 
                          ? 'bg-primary text-white shadow-xl shadow-primary/20' 
                          : 'text-muted-foreground hover:bg-muted/50'
                      }`}
                    >
                      <link.icon className="w-5 h-5" />
                      {link.name}
                    </Link>
                  ))}
                  <button
                    onClick={() => {
                      logout();
                      setIsMobileMenuOpen(false);
                    }}
                    className="w-full flex items-center gap-4 px-6 py-4 rounded-2xl text-base font-black text-danger hover:bg-danger/5 transition-smooth"
                  >
                    <LogOut className="w-5 h-5" />
                    Logout
                  </button>
                </>
              ) : (
                <div className="grid grid-cols-1 gap-4 p-4">
                  <Link
                    to="/login"
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="flex items-center justify-center py-4 rounded-2xl font-black text-muted-foreground hover:bg-muted/50 transition-smooth"
                  >
                    Login
                  </Link>
                  <Link
                    to="/register"
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="flex items-center justify-center bg-primary py-4 rounded-2xl font-black text-white shadow-xl shadow-primary/20 transition-smooth"
                  >
                    Get Started Free
                  </Link>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}
