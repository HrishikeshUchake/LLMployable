import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { FileText, Briefcase, Calendar, Download, Loader2, AlertCircle, Trash2, History, ExternalLink, Eye, X } from 'lucide-react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001';

interface Resume {
  id: string;
  job_title: string;
  github_username: string;
  created_at: string;
  is_archived: boolean;
}

interface Application {
  id: string;
  job_title: string;
  company: string;
  status: string;
  applied_date: string;
}

export default function Dashboard() {
  const { user } = useAuth();
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'resumes' | 'applications'>('resumes');
  const [previewResumeId, setPreviewResumeId] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const handleDownload = async (resumeId: string, jobTitle: string) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/user/resumes/download/${resumeId}`, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `resume_${jobTitle.replace(/\s+/g, '_')}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      console.error('Download error:', err);
      alert('Failed to download resume. Please try again.');
    }
  };

  const handlePreview = async (resumeId: string) => {
    try {
        setPreviewResumeId(resumeId);
        const response = await axios.get(`${API_BASE_URL}/api/v1/user/resumes/preview/${resumeId}`, {
          responseType: 'blob'
        });
        
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const url = window.URL.createObjectURL(blob);
        setPreviewUrl(url);
    } catch (err: any) {
        console.error('Preview error:', err);
        alert('Failed to load preview. Please try again.');
        setPreviewResumeId(null);
    }
  };

  const closePreview = () => {
    if (previewUrl) {
        window.URL.revokeObjectURL(previewUrl);
    }
    setPreviewUrl(null);
    setPreviewResumeId(null);
  };

  useEffect(() => {
    const fetchData = async () => {
      if (!user?.id) return;
      
      setLoading(true);
      try {
        const [resumesRes, appsRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/api/v1/user/resumes/${user.id}`),
          axios.get(`${API_BASE_URL}/api/v1/user/applications/${user.id}`)
        ]);
        
        setResumes(resumesRes.data);
        setApplications(appsRes.data);
      } catch (err: any) {
        setError('Failed to load dashboard data. Please try again later.');
        console.error('Dashboard fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user?.id]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <Loader2 className="w-12 h-12 text-indigo-500 animate-spin" />
        <p className="text-slate-400 animate-pulse">Loading your career overview...</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-12">
      <header className="mb-12">
        <h1 className="text-4xl font-bold text-white mb-2">Welcome, {user?.username}</h1>
        <p className="text-slate-400 text-lg">Manage your tailored resumes and track your job applications</p>
      </header>

      {error && (
        <div className="mb-8 p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center gap-3 text-red-400">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <p>{error}</p>
        </div>
      )}

      {/* Stats Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
          <div className="flex items-center gap-4 mb-2 text-indigo-400">
            <FileText className="w-5 h-5" />
            <span className="font-semibold uppercase text-xs tracking-wider">Total Resumes</span>
          </div>
          <p className="text-3xl font-bold text-white">{resumes.length}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
          <div className="flex items-center gap-4 mb-2 text-emerald-400">
            <Briefcase className="w-5 h-5" />
            <span className="font-semibold uppercase text-xs tracking-wider">Applications</span>
          </div>
          <p className="text-3xl font-bold text-white">{applications.length}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl text-slate-500 flex flex-col justify-center">
            <p className="text-sm">Keep applying to increase your chances!</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 mb-8">
        <button
          onClick={() => setActiveTab('resumes')}
          className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all ${
            activeTab === 'resumes' 
              ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/20' 
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <FileText className="w-5 h-5" />
          Resumes
        </button>
        <button
          onClick={() => setActiveTab('applications')}
          className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all ${
            activeTab === 'applications' 
              ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/20' 
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <Briefcase className="w-5 h-5" />
          Applications
        </button>
      </div>

      {/* Content */}
      <motion.div
        key={activeTab}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        {activeTab === 'resumes' ? (
          resumes.length > 0 ? (
            resumes.map(resume => (
              <div key={resume.id} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-indigo-500/50 transition-all group">
                <div className="flex justify-between items-start mb-4">
                  <div className="bg-indigo-500/10 p-3 rounded-xl text-indigo-400">
                    <History className="w-6 h-6" />
                  </div>
                  <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">
                    {new Date(resume.created_at).toLocaleDateString()}
                  </span>
                </div>
                <h3 className="text-lg font-bold text-white mb-1 group-hover:text-indigo-400 transition-colors">
                  {resume.job_title || 'Tailored Resume'}
                </h3>
                <p className="text-slate-500 text-sm mb-6 flex items-center gap-2">
                  <ExternalLink className="w-3 h-3" />
                  GitHub: {resume.github_username}
                </p>
                <div className="flex gap-2">
                  <button 
                    onClick={() => handlePreview(resume.id)}
                    className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2"
                  >
                    {previewResumeId === resume.id && !previewUrl ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                        <Eye className="w-4 h-4" />
                    )}
                    Preview
                  </button>
                  <button 
                    onClick={() => handleDownload(resume.id, resume.job_title)}
                    className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors border border-slate-700"
                    title="Download PDF"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                  <button className="p-2 border border-slate-800 hover:border-red-500/50 text-slate-500 hover:text-red-500 rounded-lg transition-colors">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="col-span-full py-20 text-center border-2 border-dashed border-slate-800 rounded-3xl">
              <FileText className="w-12 h-12 text-slate-700 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-slate-400">No resumes yet</h3>
              <p className="text-slate-600 mt-2">Generate your first tailored resume using the home page!</p>
            </div>
          )
        ) : (
          applications.length > 0 ? (
            applications.map(app => (
              <div key={app.id} className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="bg-emerald-500/10 p-3 rounded-xl text-emerald-400">
                    <Briefcase className="w-6 h-6" />
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest ${
                    app.status === 'Applied' ? 'bg-indigo-500/10 text-indigo-400' :
                    app.status === 'Interviewing' ? 'bg-amber-500/10 text-amber-400' :
                    'bg-emerald-500/10 text-emerald-400'
                  }`}>
                    {app.status}
                  </span>
                </div>
                <h3 className="text-lg font-bold text-white mb-1">{app.job_title}</h3>
                <p className="text-indigo-400 text-sm mb-4 font-medium">{app.company}</p>
                <div className="flex items-center gap-2 text-slate-500 text-sm">
                  <Calendar className="w-4 h-4" />
                  Applied on {new Date(app.applied_date).toLocaleDateString()}
                </div>
              </div>
            ))
          ) : (
            <div className="col-span-full py-20 text-center border-2 border-dashed border-slate-800 rounded-3xl">
              <Briefcase className="w-12 h-12 text-slate-700 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-slate-400">No applications tracked</h3>
              <p className="text-slate-600 mt-2">Keep track of your job search progress here.</p>
            </div>
          )
        )}
      </motion.div>

      {/* Preview Modal */}
      <AnimatePresence>
        {previewUrl && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="relative w-full max-w-5xl h-[90vh] bg-slate-900 rounded-2xl overflow-hidden flex flex-col pt-12"
            >
              <button 
                onClick={closePreview}
                className="absolute top-4 right-4 p-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl transition-colors z-10"
              >
                <X className="w-6 h-6" />
              </button>
              
              <div className="flex-1 w-full bg-white">
                <iframe 
                  src={previewUrl} 
                  className="w-full h-full border-none"
                  title="Resume Preview"
                />
              </div>
              
              <div className="p-4 bg-slate-900 border-t border-slate-800 flex justify-end gap-3">
                <button 
                    onClick={() => {
                        const link = document.createElement('a');
                        link.href = previewUrl;
                        link.setAttribute('download', 'tailored_resume.pdf');
                        link.click();
                    }}
                    className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-2 rounded-xl font-medium transition-all"
                >
                    <Download className="w-4 h-4" />
                    Download PDF
                </button>
                <button 
                    onClick={closePreview}
                    className="px-6 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-medium transition-all"
                >
                    Close
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
