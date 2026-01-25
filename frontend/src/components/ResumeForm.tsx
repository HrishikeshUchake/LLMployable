import { useState, useActionState, useEffect } from 'react';
import { Github, Linkedin, Briefcase, Download, Loader2, Rocket, AlertCircle, CheckCircle2, Info, ArrowRight, ShieldCheck } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import InterviewPrepPlan from './InterviewPrepPlan';
import LoadingProgress from './LoadingProgress';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001';

interface ActionState {
  type: 'idle' | 'loading' | 'success' | 'error';
  message: string;
  downloadUrl?: string;
  interviewPrep?: {
    tips: string[];
    technical_questions: { question: string; context: string }[];
    behavioral_questions: { question: string; context: string }[];
    situational_questions: { question: string; context: string }[];
    winning_strategy: string;
  };
}

async function generateResumeAction(_prevState: ActionState, formData: FormData): Promise<ActionState> {
  const github = formData.get('github_username') as string;
  const linkedin = formData.get('linkedin_data') as File;
  const jobDescription = formData.get('job_description') as string;

  if (!github && (!linkedin || linkedin.size === 0)) {
    return { type: 'error', message: 'Please provide at least one profile (GitHub username or LinkedIn Data Export)' };
  }

  if (!jobDescription) {
    return { type: 'error', message: 'Please provide a job description' };
  }

  try {
    let response;
    try {
      response = await axios.post(`${API_BASE_URL}/api/v1/generate-resume`, formData, {
        responseType: 'blob',
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 60000 
      });
    } catch (e: any) {
      if (e.response?.status === 404) {
        response = await axios.post(`${API_BASE_URL}/api/generate-resume`, formData, {
          responseType: 'blob',
          headers: { 'Content-Type': 'multipart/form-data' },
          timeout: 60000
        });
      } else {
        throw e;
      }
    }

    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    
    // Open preview in new tab
    window.open(url, '_blank');
    
    let interviewPrep = null;
    try {
      let prepRes;
      try {
        prepRes = await axios.post(`${API_BASE_URL}/api/v1/interview-prep`, 
          { job_description: jobDescription },
          { timeout: 35000 }
        );
      } catch (e: any) {
        if (!e.response || e.response.status === 404) {
          prepRes = await axios.post(`${API_BASE_URL}/api/interview-prep`, 
            { job_description: jobDescription },
            { timeout: 35000 }
          );
        } else {
          throw e;
        }
      }
      interviewPrep = prepRes.data;
    } catch (err: any) {
      console.error('Interview prep fetch failed:', err.message || err);
    }
    
    return { 
      type: 'success', 
      message: 'Resume generated successfully! Previews are open in a new tab.',
      downloadUrl: url,
      interviewPrep
    };
  } catch (error: any) {
    let errorMessage = 'Failed to generate resume. Please check your data and try again.';
    if (error.response?.data instanceof Blob) {
      const text = await error.response.data.text();
      try {
        const json = JSON.parse(text);
        errorMessage = json.error || errorMessage;
      } catch (e) {
        errorMessage = text || errorMessage;
      }
    } else if (error.response?.data?.error) {
      errorMessage = error.response.data.error;
    }
    return { type: 'error', message: errorMessage };
  }
}

export default function ResumeForm() {
  const { user } = useAuth();
  const [state, formAction, isPending] = useActionState(generateResumeAction, {
    type: 'idle',
    message: '',
  });

  const [fileName, setFileName] = useState<string>('');
  const [loadingStep, setLoadingStep] = useState(0);

  useEffect(() => {
    if (isPending) {
      const interval = setInterval(() => {
        setLoadingStep(s => (s + 1) % 4);
      }, 3000);
      return () => clearInterval(interval);
    } else {
      setLoadingStep(0);
    }
  }, [isPending]);

  const loadingMessages = [
    "Analyzing your technical DNA...",
    "Matching professional path to job requirements...",
    "Scanning project impact and metrics...",
    "Preparing your personalized interview coach..."
  ];

  return (
    <div className="max-w-7xl mx-auto px-4">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="lg:col-span-8"
        >
          <div className="bg-card rounded-[3rem] shadow-2xl shadow-primary/5 border border-white/10 overflow-hidden">
            <div className="p-8 sm:p-12">
              <div className="flex items-center gap-4 mb-10">
                <div className="p-3 bg-primary/10 rounded-2xl text-primary">
                    <Rocket className="w-6 h-6" />
                </div>
                <div>
                    <h2 className="text-2xl font-black">Generator Configuration</h2>
                    <p className="text-muted-foreground font-medium text-sm">Fill in your details to start the magic</p>
                </div>
              </div>

              <form action={formAction} className="space-y-10">
                {user?.id && <input type="hidden" name="user_id" value={user.id} />}

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
                  <div className="space-y-3">
                    <label htmlFor="github_username" className="text-sm font-black text-foreground flex items-center gap-2 uppercase tracking-widest">
                      <Github className="w-4 h-4 text-primary" /> GitHub Profile
                    </label>
                    <div className="relative group">
                        <input
                        type="text"
                        name="github_username"
                        id="github_username"
                        placeholder="e.g. torvalds"
                        className="w-full pl-6 pr-6 py-5 rounded-2xl bg-muted border-none focus:ring-4 focus:ring-primary/10 focus:bg-card transition-smooth outline-none font-bold text-lg placeholder:text-muted-foreground/50"
                        />
                    </div>
                  </div>

                  <div className="space-y-3">
                    <label className="text-sm font-black text-foreground flex items-center gap-2 uppercase tracking-widest">
                      <Linkedin className="w-4 h-4 text-primary" /> LinkedIn Export
                    </label>
                    <div className="relative group overflow-hidden">
                      <input
                        type="file"
                        name="linkedin_data"
                        accept=".zip"
                        onChange={(e) => setFileName(e.target.files?.[0]?.name || '')}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                      />
                      <div className="w-full px-6 py-5 rounded-2xl bg-muted border-none group-hover:bg-slate-200 transition-smooth flex items-center justify-between border-2 border-transparent group-focus-within:border-primary/20">
                        <span className={`text-lg font-bold truncate ${fileName ? 'text-primary' : 'text-muted-foreground/50'}`}>
                          {fileName || 'Upload Archive (.zip)'}
                        </span>
                        <Download className="w-5 h-5 text-muted-foreground" />
                      </div>
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  <label htmlFor="job_description" className="text-sm font-black text-foreground flex items-center gap-2 uppercase tracking-widest">
                    <Briefcase className="w-4 h-4 text-primary" /> Target Job Description
                  </label>
                  <textarea
                    name="job_description"
                    id="job_description"
                    rows={10}
                    placeholder="Describe the opportunity you're targeting..."
                    className="w-full px-6 py-6 rounded-[2rem] bg-muted border-none focus:ring-4 focus:ring-primary/10 focus:bg-card transition-smooth outline-none font-medium text-lg resize-none placeholder:text-muted-foreground/50"
                  />
                </div>

                <button
                  type="submit"
                  disabled={isPending}
                  className="w-full group relative flex items-center justify-center gap-4 py-6 px-8 rounded-2xl bg-foreground text-white font-black text-xl hover:bg-primary transition-smooth disabled:opacity-50 disabled:bg-muted shadow-2xl shadow-primary/10"
                >
                  {isPending ? (
                    <>
                      <Loader2 className="w-6 h-6 animate-spin" />
                      Generating Excellence...
                    </>
                  ) : (
                    <>
                      Begin Transformation
                      <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </>
                  )}
                </button>
              </form>

              <AnimatePresence>
                {state.type !== 'idle' && !isPending && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="mt-12"
                  >
                    <div className={`p-8 rounded-[2rem] flex items-start gap-6 border-b-4 ${
                      state.type === 'success' ? 'bg-success/5 text-success border-success/20' :
                      'bg-danger/5 text-danger border-danger/20'
                    }`}>
                      <div className={`p-3 rounded-xl ${state.type === 'success' ? 'bg-success/10' : 'bg-danger/10'}`}>
                        {state.type === 'success' ? (
                            <CheckCircle2 className="w-8 h-8" />
                        ) : (
                            <AlertCircle className="w-8 h-8" />
                        )}
                      </div>
                      <div>
                        <p className="font-black text-xl mb-1">{state.type === 'success' ? 'Great news!' : 'Process interrupted'}</p>
                        <p className="text-lg font-medium opacity-80 leading-relaxed">{state.message}</p>
                      </div>
                    </div>

                    {state.type === 'success' && state.interviewPrep && (
                      <div className="mt-12 pt-12 border-t border-muted">
                        <InterviewPrepPlan data={state.interviewPrep} />
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </motion.div>

        <div className="lg:col-span-4 space-y-8">
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-primary rounded-[3rem] p-10 text-white shadow-2xl shadow-primary/20 relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 p-8 opacity-10">
                <ShieldCheck className="w-32 h-32 rotate-12" />
            </div>
            
            <h3 className="text-2xl font-black mb-8 flex items-center gap-3">
              <Info className="w-6 h-6" /> Best Practices
            </h3>
            
            <ul className="space-y-6">
              {[
                { title: "GitHub Sync", text: "Ensure your best repositories are public for deep analysis." },
                { title: "Data Export", text: "LinkedIn ZIP exports contain your complete career timeline." },
                { title: "Target Focus", text: "High-quality job descriptions lead to 10x better matching." }
              ].map((tip, i) => (
                <li key={i} className="flex gap-4">
                  <div className="w-7 h-7 rounded-full bg-white/20 flex items-center justify-center text-xs font-black shrink-0 mt-1">
                    {i + 1}
                  </div>
                  <div>
                    <p className="font-black uppercase tracking-wider text-[10px] opacity-70 mb-1">{tip.title}</p>
                    <p className="text-sm font-medium leading-relaxed opacity-90">{tip.text}</p>
                  </div>
                </li>
              ))}
            </ul>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="glass rounded-[3rem] p-10 border border-white/10 shadow-lg group hover:shadow-xl transition-smooth"
          >
            <h3 className="text-xl font-black mb-4 group-hover:text-primary transition-colors">Privacy First</h3>
            <p className="text-muted-foreground text-sm leading-relaxed font-medium">
              We encrypt all professional data during processing. 
              {user ? (
                <span className="block mt-4 text-foreground font-bold">Resumes are automatically archived to your personal dashboard.</span>
              ) : (
                <span className="block mt-4 text-foreground font-bold">Join us to save your progress and track applications!</span>
              )}
            </p>
          </motion.div>
        </div>
      </div>

      <AnimatePresence>
        {isPending && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-foreground/30 backdrop-blur-2xl z-50 flex items-center justify-center p-6"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0, y: 30 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              className="bg-card p-12 rounded-[4rem] shadow-2xl max-w-lg w-full text-center border border-white/10"
            >
              <div className="relative w-40 h-40 mx-auto mb-10">
                <motion.div
                  className="absolute inset-0 rounded-full border-[8px] border-primary/5"
                  animate={{ scale: [1, 1.15, 1] }}
                  transition={{ duration: 4, repeat: Infinity }}
                />
                <motion.div
                  className="absolute inset-0 rounded-full border-t-[8px] border-primary"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                />
                <div className="absolute inset-0 flex items-center justify-center text-primary">
                  <motion.div
                     animate={{ 
                         y: [-8, 8, -8],
                         rotate: [0, 5, -5, 0]
                     }}
                     transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                  >
                    <Rocket className="w-16 h-16" />
                  </motion.div>
                </div>
              </div>
              
              <h3 className="text-3xl font-black mb-4">Engineering Success</h3>
              
              <AnimatePresence mode="wait">
                <motion.p 
                  key={loadingStep}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="text-muted-foreground font-bold text-lg mb-12 h-16 flex items-center justify-center px-4"
                >
                  {loadingMessages[loadingStep]}
                </motion.p>
              </AnimatePresence>
              
              <div className="space-y-6">
                 <LoadingProgress label="DNA Analysis" progress={35} />
                 <LoadingProgress label="Contextual Mapping" progress={65} />
                 <LoadingProgress label="Document Synthesis" progress={90} />
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
