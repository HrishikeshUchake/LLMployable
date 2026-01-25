import { useState, useEffect, useOptimistic } from 'react';
import { useAuth } from '../context/AuthContext';
import { 
  FileText, Briefcase, Calendar, Download, Loader2, 
  AlertCircle, Trash2, History, Eye, X,
  Plus, Search, TrendingUp, Clock, ChevronRight,
  Github, Sparkles
} from 'lucide-react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';

const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:5001');

interface Resume {
  id: string;
  job_title: string;
  job_description: string;
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
  job_description: string;
}

type JobDetailView = {
  job_title: string;
  job_description: string;
  company?: string;
};

export default function Dashboard() {
  const { user } = useAuth();
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'resumes' | 'applications'>('resumes');
  const [previewResumeId, setPreviewResumeId] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [viewingJobDetails, setViewingJobDetails] = useState<JobDetailView | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  // useOptimistic for immediate UI updates when archiving/deleting
  const [optimisticResumes, removeOptimisticResume] = useOptimistic(
    resumes,
    (state, resumeId: string) => state.filter(r => r.id !== resumeId)
  );

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
        setError('Failed to load your career data. Please check your connection.');
        console.error('Dashboard fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user?.id]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[70vh] gap-6">
        <motion.div
            animate={{ 
                scale: [1, 1.2, 1],
                rotate: [0, 180, 360]
            }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            className="w-16 h-16 rounded-2xl bg-primary/20 flex items-center justify-center"
        >
            <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </motion.div>
        <div className="text-center">
            <h2 className="text-xl font-bold">Assembling your workspace</h2>
            <p className="text-muted-foreground mt-1">This will only take a moment...</p>
        </div>
      </div>
    );
  }

  const filteredResumes = optimisticResumes.filter(r => 
    (r.job_title || '').toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto py-8">
      {/* Welcome Section */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-4xl font-black tracking-tight">
              Workspace<span className="text-accent-dot">.</span>
            </h1>
          </div>
          <p className="text-muted-foreground text-lg flex items-center gap-2">
            Welcome back, <span className="text-foreground font-black underline decoration-primary/30 decoration-4 underline-offset-4">{user?.username}</span>
          </p>
        </motion.div>
        <motion.div
           initial={{ opacity: 0, x: 20 }}
           animate={{ opacity: 1, x: 0 }}
        >
          <Link 
            to="/" 
            className="group inline-flex items-center gap-2 bg-primary hover:bg-primary-dark text-primary-foreground px-8 py-4 rounded-2xl font-black shadow-xl shadow-primary/20 transition-smooth hover:-translate-y-1 active:translate-y-0"
          >
            <Plus className="w-5 h-5 group-hover:rotate-90 transition-transform duration-300" />
            Create New Resume
          </Link>
        </motion.div>
      </div>

      {error && (
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="mb-8 p-4 bg-danger/10 border border-danger/20 rounded-2xl flex items-center gap-3 text-danger font-medium"
        >
          <AlertCircle className="w-5 h-5" />
          <p>{error}</p>
        </motion.div>
      )}

      {/* Stats Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass p-6 rounded-3xl border border-white/5 shadow-sm hover:shadow-xl transition-smooth group"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-primary/10 p-2.5 rounded-xl group-hover:scale-110 transition-transform">
                <FileText className="w-5 h-5 text-primary" />
            </div>
            <span className="text-sm font-bold text-muted-foreground uppercase tracking-wider">Resumes</span>
          </div>
          <div className="flex items-end justify-between">
            <p className="text-4xl font-black tabular-nums">{resumes.length}</p>
            <TrendingUp className="w-5 h-5 text-primary mb-1 animate-pulse" />
          </div>
        </motion.div>
        
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glass p-6 rounded-3xl border border-white/5 shadow-sm hover:shadow-xl transition-smooth group"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-success/10 p-2.5 rounded-xl group-hover:scale-110 transition-transform">
                <Briefcase className="w-5 h-5 text-success" />
            </div>
            <span className="text-sm font-bold text-muted-foreground uppercase tracking-wider">Applications</span>
          </div>
          <div className="flex items-end justify-between">
            <p className="text-4xl font-black tabular-nums">{applications.length}</p>
            <div className="bg-success text-white text-[10px] font-black px-2 py-0.5 rounded-full mb-1 shadow-sm shadow-success/20">LIVE</div>
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass p-6 rounded-3xl border border-white/5 shadow-sm hover:shadow-xl transition-smooth md:col-span-2 bg-gradient-to-br from-primary/10 via-background to-transparent flex items-center justify-between overflow-hidden relative group"
        >
            <div className="relative z-10">
                <h3 className="font-black text-foreground mb-1 flex items-center gap-2">
                    Career Insights
                    <Sparkles className="w-4 h-4 text-primary" />
                </h3>
                <p className="text-sm font-medium text-muted-foreground max-w-[280px]">You've generated <span className="text-primary font-black">{resumes.length} optimized resumes</span>. Your profile matching score is increasing!</p>
            </div>
            <Clock className="w-24 h-24 text-primary/10 absolute -right-4 -bottom-4 rotate-12 group-hover:scale-125 transition-transform duration-500" />
            <div className="absolute top-0 left-0 w-1 h-full bg-primary/20" />
        </motion.div>
      </div>

      {/* Control Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-6 mb-12 bg-muted/30 p-4 rounded-[2rem] border border-white/5">
        <div className="flex bg-background/50 backdrop-blur-sm p-1.5 rounded-2xl w-full sm:w-auto shadow-inner">
          <button
            onClick={() => setActiveTab('resumes')}
            className={`flex-1 sm:flex-none flex items-center justify-center gap-2 px-8 py-3 rounded-xl font-black text-sm transition-smooth ${
              activeTab === 'resumes' 
                ? 'bg-card text-primary shadow-lg shadow-black/5 ring-1 ring-black/5' 
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <FileText className="w-4 h-4" />
            My Resumes
          </button>
          <button
            onClick={() => setActiveTab('applications')}
            className={`flex-1 sm:flex-none flex items-center justify-center gap-2 px-8 py-3 rounded-xl font-black text-sm transition-smooth ${
              activeTab === 'applications' 
                ? 'bg-card text-primary shadow-lg shadow-black/5 ring-1 ring-black/5' 
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <Briefcase className="w-4 h-4" />
            Applications
          </button>
        </div>

        <div className="relative w-full sm:w-96 group">
            <Search className="absolute left-5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
            <input 
                type="text" 
                placeholder={`Search ${activeTab === 'resumes' ? 'resumes by job title' : 'applications'}...`}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-6 py-3.5 bg-card border-none rounded-2xl text-sm font-bold shadow-sm focus:ring-4 focus:ring-primary/10 transition-smooth placeholder:text-muted-foreground/40"
            />
            {searchQuery && (
              <button 
                onClick={() => setSearchQuery('')}
                className="absolute right-4 top-1/2 -translate-y-1/2 p-1 hover:bg-muted rounded-md transition-colors"
              >
                <X className="w-3.5 h-3.5 text-muted-foreground" />
              </button>
            )}
        </div>
      </div>

      {/* Content Area */}
      <div className="relative min-h-[400px]">
        <AnimatePresence mode="wait">
          {activeTab === 'resumes' ? (
            <motion.div
              key="resumes-tab"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
            >
            {filteredResumes.length > 0 ? (
              filteredResumes.map(resume => (
                <motion.div 
                  key={resume.id} 
                  layout
                  className="group bg-card border border-white/10 rounded-[2rem] p-8 shadow-sm hover:shadow-xl hover:shadow-primary/5 hover:border-primary/20 transition-smooth overflow-hidden relative"
                >
                  <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-100 transition-opacity">
                    <History className="w-12 h-12 text-primary -rotate-12" />
                  </div>

                  <div className="flex justify-between items-start mb-6">
                    <button 
                      onClick={() => setViewingJobDetails(resume)}
                      className="p-3.5 bg-muted rounded-2xl text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-smooth shadow-inner cursor-pointer hover:scale-105"
                      title="View Job Details"
                    >
                      <FileText className="w-6 h-6" />
                    </button>
                    <span className="text-[10px] text-muted-foreground uppercase font-black tracking-widest bg-muted/50 px-2 py-1 rounded-md">
                      {new Date(resume.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                    </span>
                  </div>

                  <h3 className="text-xl font-black mb-2 leading-tight group-hover:text-primary transition-colors">
                    {resume.job_title || 'Tailored Resume'}
                  </h3>
                  
                  <div className="flex items-center gap-2 text-muted-foreground text-xs font-bold mb-8">
                    <Github className="w-3.5 h-3.5 text-foreground" />
                    <span>{resume.github_username}</span>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <button 
                      onClick={() => handlePreview(resume.id)}
                      className="bg-primary hover:bg-primary-dark text-primary-foreground py-3 rounded-2xl text-sm font-black transition-smooth flex items-center justify-center gap-2 shadow-lg shadow-primary/20"
                    >
                      {previewResumeId === resume.id && !previewUrl ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                          <Eye className="w-4 h-4" />
                      )}
                      Preview
                    </button>
                    <div className="flex gap-2">
                       <button 
                        onClick={() => handleDownload(resume.id, resume.job_title)}
                        className="flex-1 bg-muted hover:bg-muted/80 text-foreground py-3 rounded-2xl transition-smooth flex items-center justify-center border border-transparent hover:border-white/20"
                        title="Download PDF"
                      >
                        <Download className="w-4 h-4" />
                      </button>
                      <button 
                        className="flex-1 bg-danger/5 hover:bg-danger text-danger hover:text-white p-3 rounded-2xl transition-smooth border border-danger/10"
                        onClick={() => removeOptimisticResume(resume.id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))
            ) : (
              <div className="col-span-full py-32 text-center rounded-[3rem] border-2 border-dashed border-muted flex flex-col items-center">
                <div className="w-20 h-20 bg-muted rounded-3xl flex items-center justify-center mb-6">
                    <FileText className="w-10 h-10 text-muted-foreground" />
                </div>
                <h3 className="text-2xl font-black">Ready to launch?</h3>
                <p className="text-muted-foreground mt-2 max-w-sm font-medium">
                  {searchQuery ? `No resumes matching "${searchQuery}"` : "You haven't generated any tailored resumes yet. Let's build something great."}
                </p>
                {!searchQuery && (
                  <Link to="/" className="mt-8 text-primary font-bold flex items-center gap-2 hover:gap-3 transition-all">
                    Generate now <ChevronRight className="w-4 h-4" />
                  </Link>
                )}
              </div>
            )}
          </motion.div>
        ) : (
          <motion.div
            key="applications-tab"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
          >
            {applications.length > 0 ? (
              applications.map(app => (
                <div key={app.id} className="bg-card border border-white/10 rounded-[2rem] p-8 shadow-sm hover:shadow-xl transition-smooth relative overflow-hidden group">
                  <div className="flex justify-between items-start mb-6">
                    <button 
                      onClick={() => setViewingJobDetails({ job_title: app.job_title, job_description: app.job_description, company: app.company })}
                      className="p-3.5 bg-success/10 rounded-2xl text-success shadow-inner hover:bg-success hover:text-white transition-smooth"
                    >
                      <Briefcase className="w-6 h-6" />
                    </button>
                    <span className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest shadow-sm ${
                      app.status === 'Applied' ? 'bg-primary/10 text-primary' :
                      app.status === 'Interviewing' ? 'bg-warning/10 text-warning' :
                      'bg-success/10 text-success'
                    }`}>
                      {app.status}
                    </span>
                  </div>
                  <h3 className="text-xl font-black mb-1 group-hover:text-primary transition-colors">{app.job_title}</h3>
                  <p className="text-primary font-bold text-sm mb-6">{app.company}</p>
                  
                  <div className="flex items-center justify-between border-t border-muted pt-6 mt-2">
                    <div className="flex items-center gap-2 text-muted-foreground text-xs font-bold">
                      <Calendar className="w-3.5 h-3.5" />
                      {new Date(app.applied_date).toLocaleDateString()}
                    </div>
                    <button 
                      onClick={() => setViewingJobDetails({ job_title: app.job_title, job_description: app.job_description, company: app.company })}
                      className="text-xs font-black text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1 group/btn"
                    >
                        Details <ChevronRight className="w-3 h-3 group-hover/btn:translate-x-1 transition-transform" />
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <div className="col-span-full py-32 text-center rounded-[3rem] border-2 border-dashed border-muted flex flex-col items-center">
                <div className="w-20 h-20 bg-muted rounded-3xl flex items-center justify-center mb-6">
                    <Briefcase className="w-10 h-10 text-muted-foreground" />
                </div>
                <h3 className="text-2xl font-black">Track your journey</h3>
                <p className="text-muted-foreground mt-2 max-w-sm font-medium">Keep track of every application and increase your chances of success.</p>
              </div>
            )}
          </motion.div>
        )}
        </AnimatePresence>
      </div>

      {/* Modern Preview Modal */}
      <AnimatePresence>
        {previewUrl && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-8 bg-foreground/90 backdrop-blur-md">
            <motion.div 
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="relative w-full max-w-6xl h-full bg-card rounded-[2.5rem] overflow-hidden flex flex-col shadow-2xl border border-white/10"
            >
              <div className="bg-card w-full px-8 py-4 border-b border-muted flex items-center justify-between">
                <div>
                    <h2 className="text-lg font-black flex items-center gap-2 text-foreground">
                        <FileText className="w-5 h-5 text-primary" />
                        Live Preview
                    </h2>
                </div>
                <button 
                    onClick={closePreview}
                    className="p-2.5 bg-muted hover:bg-muted/80 text-foreground rounded-xl transition-smooth"
                >
                    <X className="w-5 h-5" />
                </button>
              </div>
              
              <div className="flex-1 w-full bg-muted/50/50 p-4 sm:p-8 overflow-auto flex justify-center">
                <motion.div 
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="w-full max-w-4xl h-full bg-white shadow-2xl rounded-lg overflow-hidden"
                >
                    <iframe 
                    src={previewUrl} 
                    className="w-full h-full border-none"
                    title="Resume Preview"
                    />
                </motion.div>
              </div>
              
              <div className="p-6 bg-card border-t border-muted flex flex-col sm:flex-row justify-center items-center gap-4">
                <button 
                    onClick={() => {
                        const link = document.createElement('a');
                        link.href = previewUrl;
                        link.setAttribute('download', 'tailored_resume.pdf');
                        link.click();
                    }}
                    className="w-full sm:w-auto flex items-center justify-center gap-3 bg-primary hover:bg-primary-dark text-primary-foreground px-10 py-3.5 rounded-2xl font-black shadow-xl shadow-primary/25 transition-smooth"
                >
                    <Download className="w-5 h-5" />
                    Download PDF Document
                </button>
                <button 
                    onClick={closePreview}
                    className="w-full sm:w-auto px-10 py-3.5 bg-muted hover:bg-muted/80 text-foreground rounded-2xl font-bold transition-smooth"
                >
                    Dismiss
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Job Details Modal */}
      <AnimatePresence>
        {viewingJobDetails && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-8 bg-foreground/80 backdrop-blur-sm">
            <motion.div 
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="relative w-full max-w-2xl bg-card rounded-[2.5rem] overflow-hidden flex flex-col shadow-2xl border border-white/10"
            >
              <div className="bg-card w-full px-8 py-6 border-b border-muted flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-black flex items-center gap-2 text-foreground">
                    <Briefcase className="w-6 h-6 text-primary" />
                    Job Details
                  </h2>
                  <p className="text-sm text-muted-foreground font-medium mt-1">
                    {viewingJobDetails.company ? `Application for ${viewingJobDetails.company}` : `Uploaded for ${viewingJobDetails.job_title}`}
                  </p>
                </div>
                <button 
                  onClick={() => setViewingJobDetails(null)}
                  className="p-2.5 bg-muted hover:bg-muted/80 text-foreground rounded-xl transition-smooth"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <div className="flex-1 p-8 overflow-y-auto max-h-[60vh]">
                <div className="prose prose-sm max-w-none">
                  <h4 className="text-foreground font-bold mb-2 uppercase tracking-wider text-xs">Role Title</h4>
                  <p className="text-lg font-bold mb-6">{viewingJobDetails.job_title}</p>
                  
                  <h4 className="text-foreground font-bold mb-2 uppercase tracking-wider text-xs">Original Job Description</h4>
                  <div className="bg-muted/50 p-6 rounded-2xl text-muted-foreground whitespace-pre-wrap leading-relaxed text-sm border border-white/5">
                    {viewingJobDetails.job_description || "No description provided."}
                  </div>
                </div>
              </div>
              
              <div className="p-6 bg-card border-t border-muted flex justify-end">
                <button 
                  onClick={() => setViewingJobDetails(null)}
                  className="px-8 py-3 bg-primary hover:bg-primary-dark text-primary-foreground rounded-2xl font-bold transition-smooth shadow-lg shadow-primary/20"
                >
                  Close Details
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
