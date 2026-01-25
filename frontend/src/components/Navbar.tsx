import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Rocket, LogIn, UserPlus, LogOut, LayoutDashboard } from 'lucide-react';

export default function Navbar() {
  const { user, logout, isAuthenticated } = useAuth();

  return (
    <nav className="bg-slate-900 border-b border-slate-800 px-6 py-4 flex items-center justify-between">
      <Link to="/" className="flex items-center gap-2 group">
        <div className="bg-indigo-600 p-2 rounded-lg group-hover:rotate-12 transition-transform">
          <Rocket className="w-5 h-5 text-white" />
        </div>
        <span className="text-xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
          Mployable
        </span>
      </Link>

      <div className="flex items-center gap-6">
        {isAuthenticated ? (
          <>
            <Link to="/dashboard" className="flex items-center gap-2 text-slate-300 hover:text-white transition-colors">
              <LayoutDashboard className="w-4 h-4" />
              <span>Dashboard</span>
            </Link>
            <div className="flex items-center gap-4 pl-6 border-l border-slate-800">
              <span className="text-sm text-slate-400">Hi, {user?.username}</span>
              <button
                onClick={logout}
                className="flex items-center gap-2 text-sm font-medium text-slate-300 hover:text-red-400 transition-colors"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          </>
        ) : (
          <>
            <Link 
              to="/login" 
              className="flex items-center gap-2 text-slate-300 hover:text-white transition-colors"
            >
              <LogIn className="w-4 h-4" />
              <span>Login</span>
            </Link>
            <Link 
              to="/register" 
              className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-all"
            >
              <UserPlus className="w-4 h-4" />
              <span>Get Started</span>
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
