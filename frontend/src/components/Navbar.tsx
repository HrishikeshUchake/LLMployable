import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Rocket, LogOut, LayoutDashboard, Menu, X } from 'lucide-react';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Navbar() {
  const { user, logout, isAuthenticated } = useAuth();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navLinks = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard, protected: true },
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
                <Rocket className="w-5 h-5 text-white" />
              </motion.div>
              <span className="text-2xl font-black tracking-tight text-foreground">
                Mployable<span className="text-primary">.</span>
              </span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            {isAuthenticated && (
              <div className="flex items-center gap-6">
                {navLinks.map((link) => (
                  <Link
                    key={link.path}
                    to={link.path}
                    className={`flex items-center gap-2 text-sm font-semibold transition-smooth ${
                      location.pathname === link.path 
                        ? 'text-primary' 
                        : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    <link.icon className="w-4 h-4" />
                    {link.name}
                  </Link>
                ))}
              </div>
            )}

            <div className="flex items-center gap-4 ml-4 pl-4 border-l border-white/10">
              {isAuthenticated ? (
                <div className="flex items-center gap-6">
                  <div className="flex flex-col items-end">
                    <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Member</span>
                    <span className="text-sm font-semibold text-foreground">{user?.username}</span>
                  </div>
                  <button
                    onClick={logout}
                    className="flex items-center gap-2 text-sm font-bold text-muted-foreground hover:text-danger transition-smooth bg-muted px-4 py-2 rounded-xl"
                  >
                    <LogOut className="w-4 h-4" />
                    Logout
                  </button>
                </div>
              ) : (
                <div className="flex items-center gap-3">
                  <Link 
                    to="/login" 
                    className="px-4 py-2 text-sm font-bold text-muted-foreground hover:text-foreground transition-smooth"
                  >
                    Login
                  </Link>
                  <Link 
                    to="/register" 
                    className="bg-primary hover:bg-primary-dark text-white px-5 py-2.5 rounded-xl text-sm font-bold shadow-lg shadow-primary/25 transition-smooth"
                  >
                    Sign Up Free
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

      {/* Mobile menu */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden border-t border-white/10 bg-background/95 backdrop-blur-md overflow-hidden"
          >
            <div className="px-4 pt-2 pb-6 space-y-1">
              {isAuthenticated ? (
                <>
                  <Link
                    to="/dashboard"
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="block px-3 py-4 text-base font-bold text-foreground border-b border-white/5"
                  >
                    Dashboard
                  </Link>
                  <div className="pt-4 flex items-center justify-between">
                    <span className="text-sm font-semibold text-muted-foreground">{user?.username}</span>
                    <button
                      onClick={() => {
                        logout();
                        setIsMobileMenuOpen(false);
                      }}
                      className="text-sm font-bold text-danger"
                    >
                      Logout
                    </button>
                  </div>
                </>
              ) : (
                <div className="grid grid-cols-2 gap-4 pt-4">
                  <Link
                    to="/login"
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="flex items-center justify-center px-4 py-3 rounded-xl font-bold bg-muted text-foreground"
                  >
                    Login
                  </Link>
                  <Link
                    to="/register"
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="flex items-center justify-center px-4 py-3 rounded-xl font-bold bg-primary text-white"
                  >
                    Sign Up
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
