import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Mail, Lock, User, Loader2, AlertCircle, CheckCircle2, BadgeCheck } from 'lucide-react';
import axios from 'axios';
import { motion } from 'framer-motion';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001';

export default function RegisterForm() {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    first_name: '',
    last_name: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await axios.post(`${API_BASE_URL}/api/v1/auth/register`, formData);
      setSuccess(true);
      setTimeout(() => navigate('/login'), 2000);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4 py-12 bg-background">
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-2xl w-full glass rounded-[3rem] p-10 shadow-2xl border border-white/10"
      >
        <div className="text-center mb-12">
          <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <User className="w-8 h-8 text-primary" />
          </div>
          <h2 className="text-3xl font-black mb-2">Join Mployable</h2>
          <p className="text-muted-foreground font-medium">Bridge the gap between your talent and your career</p>
        </div>

        {success ? (
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-12"
          >
            <div className="bg-success text-white w-20 h-20 rounded-[2rem] flex items-center justify-center mx-auto mb-6 shadow-xl shadow-success/20">
              <BadgeCheck className="w-10 h-10" />
            </div>
            <h3 className="text-2xl font-black mb-2">Welcome Aboard!</h3>
            <p className="text-muted-foreground font-medium leading-relaxed">
                Your account has been created successfully.<br />
                Redirecting to secure login...
            </p>
          </motion.div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-8">
            {error && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="p-4 bg-danger/5 border border-danger/10 rounded-2xl flex items-center gap-3 text-danger text-sm font-bold"
              >
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                <p>{error}</p>
              </motion.div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-xs font-black uppercase tracking-widest text-muted-foreground ml-1">First Name</label>
                <input
                  name="first_name"
                  type="text"
                  value={formData.first_name}
                  onChange={handleChange}
                  className="w-full bg-muted/50 border-none rounded-2xl py-4 px-6 font-bold text-foreground placeholder:text-muted-foreground/30 focus:ring-4 focus:ring-primary/10 focus:bg-card transition-smooth outline-none"
                  placeholder="John"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-black uppercase tracking-widest text-muted-foreground ml-1">Last Name</label>
                <input
                  name="last_name"
                  type="text"
                  value={formData.last_name}
                  onChange={handleChange}
                  className="w-full bg-muted/50 border-none rounded-2xl py-4 px-6 font-bold text-foreground placeholder:text-muted-foreground/30 focus:ring-4 focus:ring-primary/10 focus:bg-card transition-smooth outline-none"
                  placeholder="Doe"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-black uppercase tracking-widest text-muted-foreground ml-1">Username</label>
              <div className="relative group">
                <User className="absolute left-6 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
                <input
                  name="username"
                  type="text"
                  value={formData.username}
                  onChange={handleChange}
                  className="w-full bg-muted/50 border-none rounded-2xl py-4 pl-14 pr-6 font-bold text-foreground placeholder:text-muted-foreground/30 focus:ring-4 focus:ring-primary/10 focus:bg-card transition-smooth outline-none"
                  placeholder="developer_pro"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-black uppercase tracking-widest text-muted-foreground ml-1">Email Address</label>
              <div className="relative group">
                <Mail className="absolute left-6 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
                <input
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full bg-muted/50 border-none rounded-2xl py-4 pl-14 pr-6 font-bold text-foreground placeholder:text-muted-foreground/30 focus:ring-4 focus:ring-primary/10 focus:bg-card transition-smooth outline-none"
                  placeholder="john@example.com"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-black uppercase tracking-widest text-muted-foreground ml-1">Secure Password</label>
              <div className="relative group">
                <Lock className="absolute left-6 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
                <input
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full bg-muted/50 border-none rounded-2xl py-4 pl-14 pr-6 font-bold text-foreground placeholder:text-muted-foreground/30 focus:ring-4 focus:ring-primary/10 focus:bg-card transition-smooth outline-none"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-foreground hover:bg-primary disabled:opacity-50 text-white font-black py-5 rounded-[2rem] transition-smooth shadow-2xl shadow-primary/10 flex items-center justify-center gap-3 mt-10"
            >
              {loading ? (
                <>
                  <Loader2 className="w-6 h-6 animate-spin" />
                  Creating Account...
                </>
              ) : (
                'Launch My Journey'
              )}
            </button>

            <div className="mt-8 text-center">
                <p className="text-muted-foreground font-medium text-sm">
                    Already part of the community?{' '}
                    <Link to="/login" className="text-primary font-black hover:underline underline-offset-4">
                    Sign in here
                    </Link>
                </p>
            </div>
          </form>
        )}
      </motion.div>
    </div>
  );
}
