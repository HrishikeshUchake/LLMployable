import { useState, useActionState, useTransition, useCallback, useRef, useEffect } from 'react'
import { Rocket, Github, Linkedin, Briefcase, Download, Loader2, AlertCircle, CheckCircle2, Info, Lightbulb, MessageSquare, Brain, Trophy, ChevronRight, Copy, Check, ChevronDown, ChevronUp } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'

// API Base URL - adjust if backend is on different port
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001'

interface ActionState {
  type: 'idle' | 'loading' | 'success' | 'error'
  message: string
  downloadUrl?: string
  interviewPrep?: {
    tips: string[];
    technical_questions: { question: string; context: string }[];
    behavioral_questions: { question: string; context: string }[];
    situational_questions: { question: string; context: string }[];
    winning_strategy: string;
  }
}

async function generateResumeAction(prevState: ActionState, formData: FormData): Promise<ActionState> {
  const github = formData.get('github_username') as string
  const linkedin = formData.get('linkedin_data') as File
  const jobDescription = formData.get('job_description') as string

  if (!github && (!linkedin || linkedin.size === 0)) {
    return { type: 'error', message: 'Please provide at least one profile (GitHub username or LinkedIn Data Export)' }
  }

  if (!jobDescription) {
    return { type: 'error', message: 'Please provide a job description' }
  }

  try {
    // Stage 1: Generate Resume (Main task)
    let response;
    try {
      response = await axios.post(`${API_BASE_URL}/api/v1/generate-resume`, formData, {
        responseType: 'blob',
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 60000 // 60s timeout
      })
    } catch (e: any) {
      if (e.response?.status === 404) {
        response = await axios.post(`${API_BASE_URL}/api/generate-resume`, formData, {
          responseType: 'blob',
          headers: { 'Content-Type': 'multipart/form-data' },
          timeout: 60000
        })
      } else {
        throw e;
      }
    }

    const blob = new Blob([response.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    
    // Auto-download logic
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'tailored_resume.pdf')
    document.body.appendChild(link)
    link.click()
    link.parentNode?.removeChild(link)

    // Stage 2: Fetch Interview Prep (Sequential to avoid race conditions/timeouts)
    let interviewPrep = null;
    try {
      console.log('Fetching interview prep...');
      let prepRes;
      try {
        prepRes = await axios.post(`${API_BASE_URL}/api/v1/interview-prep`, 
          { job_description: jobDescription },
          { timeout: 35000 }
        );
      } catch (e: any) {
        console.warn('V1 interview prep failed, trying fallback...', e.message);
        // Fallback if 404 OR if it's a network/CORS error (which might happen if preflight fails on V1)
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
      console.log('Interview prep loaded successfully');
    } catch (err: any) {
      console.error('Interview prep fetch failed:', err.message || err);
      // We don't throw here so the user still sees the success for the resume
    }
    
    return { 
      type: 'success', 
      message: 'Resume generated! Your download should start automatically.',
      downloadUrl: url,
      interviewPrep
    }
  } catch (error: any) {
    console.error('Error generating resume:', error)
    
    let errorMessage = 'Failed to generate resume. Please try again.'
    
    if (error.response?.data instanceof Blob) {
      // Convert Blob error back to JSON
      const text = await error.response.data.text()
      try {
        const json = JSON.parse(text)
        errorMessage = json.error || errorMessage
      } catch (e) {
        errorMessage = text || errorMessage
      }
    } else if (error.response?.data?.error) {
      errorMessage = error.response.data.error
    } else if (error.message) {
      errorMessage = error.message
    }
    
    return { type: 'error', message: errorMessage }
  }
}

function QuestionCard({ question, context, index }: { question: string; context: string; index: number }) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="group bg-slate-50 border border-slate-100 rounded-2xl overflow-hidden hover:border-indigo-200 hover:shadow-md transition-all cursor-pointer"
      onClick={() => setIsOpen(!isOpen)}
    >
      <div className="p-4 flex items-start justify-between gap-4">
        <div className="flex gap-4">
          <span className="flex-shrink-0 w-6 h-6 rounded-full bg-white border border-slate-200 text-[10px] font-bold flex items-center justify-center text-slate-400 group-hover:text-indigo-600 group-hover:border-indigo-100 transition-colors">
            {index + 1}
          </span>
          <p className="font-bold text-slate-800 text-sm leading-relaxed tracking-tight group-hover:text-slate-900 transition-colors">
            {question}
          </p>
        </div>
        <div className="flex-shrink-0 mt-1">
          {isOpen ? (
            <ChevronUp className="w-4 h-4 text-slate-400 group-hover:text-indigo-500 transition-colors" />
          ) : (
            <ChevronDown className="w-4 h-4 text-slate-400 group-hover:text-indigo-500 transition-colors" />
          )}
        </div>
      </div>
      
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            <div className="px-12 pb-4 pt-1">
              <div className="p-3 rounded-xl bg-white border border-slate-100 flex gap-3 shadow-sm">
                <div className="bg-indigo-50 p-1.5 rounded-lg flex-shrink-0 h-fit mt-0.5">
                  <Info className="w-3.5 h-3.5 text-indigo-600" />
                </div>
                <div>
                  <p className="text-[10px] font-bold text-indigo-900 uppercase tracking-wider mb-1">Coach Context</p>
                  <p className="text-sm text-slate-600 font-medium leading-relaxed italic">
                    {context}
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

function App() {
  const [state, formAction, isPending] = useActionState(generateResumeAction, {
    type: 'idle',
    message: '',
  })

  // Local state for UI feedback
  const [fileName, setFileName] = useState<string>('')
  
  // Dynamic loading message
  const [loadingStep, setLoadingStep] = useState(0)
  
  useEffect(() => {
    if (isPending) {
      const interval = setInterval(() => {
        setLoadingStep(s => (s + 1) % 4)
      }, 3000)
      return () => clearInterval(interval)
    } else {
      setLoadingStep(0)
    }
  }, [isPending])

  const loadingMessages = [
    "Analyzing your technical DNA...",
    "Matching professional path to job requirements...",
    "Scanning project impact and metrics...",
    "Preparing your personalized interview coach..."
  ]

  return (
    <div className="min-h-screen bg-[#fafafa] text-slate-900 py-12 px-4 sm:px-6 lg:px-8 selection:bg-indigo-100 selection:text-indigo-700">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
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

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Form Area */}
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="lg:col-span-2 space-y-8"
          >
            <div className="bg-white rounded-[2rem] shadow-2xl overflow-hidden border border-slate-100">
              <div className="p-8 sm:p-10">
                <form action={formAction} className="space-y-8">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    {/* GitHub Input */}
                    <div className="space-y-2">
                      <label htmlFor="github_username" className="text-sm font-bold text-slate-800 flex items-center gap-2">
                        <Github className="w-4 h-4 text-indigo-600" /> GitHub Profile
                      </label>
                      <input
                        type="text"
                        name="github_username"
                        id="github_username"
                        placeholder="e.g. torvalds"
                        className="w-full px-5 py-4 rounded-2xl bg-slate-50 border border-slate-200 focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all outline-none font-medium"
                      />
                    </div>

                    {/* LinkedIn File Input */}
                    <div className="space-y-2">
                      <label className="text-sm font-bold text-slate-800 flex items-center gap-2">
                        <Linkedin className="w-4 h-4 text-indigo-600" /> LinkedIn Export
                      </label>
                      <div className="relative group">
                        <input
                          type="file"
                          name="linkedin_data"
                          accept=".zip"
                          onChange={(e) => setFileName(e.target.files?.[0]?.name || '')}
                          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                        />
                        <div className="w-full px-5 py-4 rounded-2xl bg-slate-50 border border-slate-200 group-hover:border-indigo-300 transition-all flex items-center justify-between overflow-hidden">
                          <span className={`text-sm truncate ${fileName ? 'text-indigo-600 font-bold' : 'text-slate-400'}`}>
                            {fileName || 'Upload .zip export'}
                          </span>
                          <Download className="w-4 h-4 text-slate-400 shrink-0" />
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Job Description */}
                  <div className="space-y-2">
                    <label htmlFor="job_description" className="text-sm font-bold text-slate-800 flex items-center gap-2">
                      <Briefcase className="w-4 h-4 text-indigo-600" /> Target Job Description
                    </label>
                    <textarea
                      name="job_description"
                      id="job_description"
                      rows={8}
                      placeholder="Paste the job requirements, responsibilities, and details here..."
                      className="w-full px-5 py-4 rounded-2xl bg-slate-50 border border-slate-200 focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all outline-none font-medium resize-none"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={isPending}
                    className="w-full group relative flex items-center justify-center gap-3 py-5 px-8 rounded-2xl bg-slate-900 text-white font-bold text-xl hover:bg-indigo-600 transition-all duration-300 disabled:opacity-50 disabled:bg-slate-400 shadow-xl shadow-slate-200"
                  >
                    {isPending ? (
                      <>
                        <Loader2 className="w-6 h-6 animate-spin" />
                        Crafting Resume...
                      </>
                    ) : (
                      <>
                        <Rocket className="w-5 h-5 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                        Generate Now
                      </>
                    )}
                  </button>
                </form>

                <AnimatePresence>
                  {state.type !== 'idle' && !isPending && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0 }}
                      className="mt-8"
                    >
                      <div className={`p-5 rounded-2xl flex items-start gap-4 ${
                        state.type === 'success' ? 'bg-emerald-50 text-emerald-800 border border-emerald-100' :
                        'bg-rose-50 text-rose-800 border border-rose-100'
                      }`}>
                        {state.type === 'success' ? (
                          <CheckCircle2 className="w-6 h-6 mt-0.5 shrink-0 text-emerald-600" />
                        ) : (
                          <AlertCircle className="w-6 h-6 mt-0.5 shrink-0 text-rose-600" />
                        )}
                        <div>
                          <p className="font-bold text-base mb-1">{state.type === 'success' ? 'Success!' : 'Oops!'}</p>
                          <p className="text-sm opacity-90 leading-relaxed font-medium">{state.message}</p>
                        </div>
                      </div>

                      {state.type === 'success' && (
                        <div className="mt-8">
                          {state.interviewPrep ? (
                            <InterviewPrepPlan data={state.interviewPrep} />
                          ) : (
                            <motion.div 
                              initial={{ opacity: 0, scale: 0.95 }}
                              animate={{ opacity: 1, scale: 1 }}
                              className="p-8 bg-amber-50/50 border border-amber-100 rounded-[2rem] text-center"
                            >
                              <AlertCircle className="w-10 h-10 text-amber-500 mx-auto mb-4" />
                              <h4 className="text-amber-900 font-black text-xl mb-2 tracking-tight">Interview Prep Unavailable</h4>
                              <p className="text-amber-800/80 text-sm font-medium max-w-sm mx-auto leading-relaxed">
                                We couldn't generate your preparation plan this time, but your tailored resume is ready!
                              </p>
                            </motion.div>
                          )}
                        </div>
                      )}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </motion.div>

          {/* Sidebar / Info Area */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="space-y-6"
          >
            <div className="bg-indigo-600 rounded-[2rem] p-8 text-white shadow-xl shadow-indigo-100">
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Info className="w-5 h-5" /> Quick Tips
              </h3>
              <ul className="space-y-4 text-indigo-50 leading-relaxed text-sm font-medium">
                <li className="flex gap-3">
                  <div className="w-5 h-5 rounded-full bg-white/20 flex items-center justify-center text-xs shrink-0">1</div>
                  Use a real GitHub username for better project analysis.
                </li>
                <li className="flex gap-3">
                  <div className="w-5 h-5 rounded-full bg-white/20 flex items-center justify-center text-xs shrink-0">2</div>
                  LinkedIn ZIP export provides the most accurate professional history.
                </li>
                <li className="flex gap-3">
                  <div className="w-5 h-5 rounded-full bg-white/20 flex items-center justify-center text-xs shrink-0">3</div>
                  Include the "Benefits" and "Company Mission" in the JD for context.
                </li>
              </ul>
            </div>

            <div className="bg-white rounded-[2rem] p-8 border border-slate-100 shadow-lg">
              <h3 className="text-lg font-bold text-slate-800 mb-2">Security Note</h3>
              <p className="text-slate-500 text-sm leading-relaxed font-medium">
                We don't store your LinkedIn ZIP or GitHub history. Data is processed in real-time and deleted immediately after resume generation.
              </p>
            </div>
          </motion.div>
        </div>

        <p className="mt-16 text-center text-sm font-bold text-slate-400 uppercase tracking-widest flex items-center justify-center gap-2">
          Powered by <span className="text-slate-600">Google Gemini</span> &bull; Built for <span className="text-indigo-600">The Future of Work</span>
        </p>
      </div>

      {/* Modern Loading Overlay */}
      <AnimatePresence>
        {isPending && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-slate-900/40 backdrop-blur-xl z-50 flex items-center justify-center p-4"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              className="bg-white p-10 rounded-[3rem] shadow-[0_32px_64px_-12px_rgba(0,0,0,0.2)] max-w-sm w-full text-center"
            >
              <div className="relative w-32 h-32 mx-auto mb-8">
                <motion.div
                  className="absolute inset-0 rounded-full border-[6px] border-indigo-50"
                  animate={{ scale: [1, 1.1, 1] }}
                  transition={{ duration: 3, repeat: Infinity }}
                />
                <motion.div
                  className="absolute inset-0 rounded-full border-t-[6px] border-indigo-600"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                />
                <div className="absolute inset-0 flex items-center justify-center text-indigo-600">
                  <motion.div
                     animate={{ y: [-4, 4, -4] }}
                     transition={{ duration: 2, repeat: Infinity }}
                  >
                    <Rocket className="w-14 h-14" />
                  </motion.div>
                </div>
              </div>
              <h3 className="text-2xl font-black text-slate-900 mb-3">Forging Success</h3>
              <AnimatePresence mode="wait">
                <motion.p 
                  key={loadingStep}
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -5 }}
                  className="text-slate-500 font-medium mb-8 h-12 flex items-center justify-center leading-relaxed"
                >
                  {loadingMessages[loadingStep]}
                </motion.p>
              </AnimatePresence>
              
              <div className="grid grid-cols-1 gap-4">
                 <LoadingProgress label="Scanning Tech Stack" progress={35} />
                 <LoadingProgress label="Analyzing Professional Impact" progress={65} />
                 <LoadingProgress label="Generating LaTeX Assets" progress={90} />
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

function InterviewPrepPlan({ data }: { data: NonNullable<ActionState['interviewPrep']> }) {
  const [copied, setCopied] = useState(false)

  // Defensive values
  const tips = Array.isArray(data?.tips) ? data.tips : []
  const techQs = Array.isArray(data?.technical_questions) ? data.technical_questions : []
  const behavioralQs = Array.isArray(data?.behavioral_questions) ? data.behavioral_questions : []
  const situationalQs = Array.isArray(data?.situational_questions) ? data.situational_questions : []
  const winningStrategy = data?.winning_strategy || 'Be prepared and stay confident.'

  const copyToClipboard = () => {
    try {
      const text = `
INTERVIEW PREP PLAN
-------------------
WINNING STRATEGY:
${winningStrategy}

PREP TIPS:
${tips.map(t => `- ${t}`).join('\n')}

TECHNICAL QUESTIONS:
${techQs.map((q, i) => `${i+1}. ${q?.question}\n   Context: ${q?.context}`).join('\n\n')}

BEHAVIORAL QUESTIONS:
${behavioralQs.map((q, i) => `${i+1}. ${q?.question}\n   Context: ${q?.context}`).join('\n\n')}
`.trim()

      navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy text:', err)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="mt-8 space-y-6"
    >
      <div className="bg-white rounded-[2rem] border border-slate-100 shadow-xl overflow-hidden">
        <div className="bg-slate-900 p-6 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Trophy className="w-6 h-6 text-indigo-400" />
            <h3 className="text-xl font-black tracking-tight text-white mb-0">Interview Game Plan</h3>
          </div>
          <button 
            type="button"
            onClick={copyToClipboard}
            className="flex items-center gap-2 bg-white/10 hover:bg-white/20 px-4 py-2 rounded-xl transition-all text-sm font-bold border border-white/10"
          >
            {copied ? (
              <><Check className="w-4 h-4 text-emerald-400" /> Copied!</>
            ) : (
              <><Copy className="w-4 h-4" /> Copy Plan</>
            )}
          </button>
        </div>
        
        <div className="p-8 space-y-10">
          {/* Winning Strategy */}
          <div className="relative group">
            <div className="absolute -inset-4 bg-indigo-50/50 rounded-[2rem] -z-10 group-hover:bg-indigo-50 transition-colors" />
            <h4 className="text-indigo-900 font-bold mb-3 flex items-center gap-2 text-lg">
              <Lightbulb className="w-6 h-6 text-indigo-600" /> Winning Strategy
            </h4>
            <p className="text-indigo-800 text-sm leading-relaxed font-semibold italic">
              "{winningStrategy}"
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Tips Section */}
            <div className="space-y-4">
              <h4 className="text-slate-900 font-black text-sm uppercase tracking-widest flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-indigo-600" /> Actionable Tips
              </h4>
              <div className="space-y-3">
                {tips.length > 0 ? tips.map((tip, i) => (
                  <motion.div 
                    key={i} 
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className="flex gap-3 p-4 rounded-2xl bg-slate-50 border border-slate-100 items-start hover:border-indigo-100 transition-colors"
                  >
                    <div className="mt-1 w-1.5 h-1.5 rounded-full bg-indigo-600 shrink-0" />
                    <p className="text-sm text-slate-700 font-medium leading-relaxed">{tip}</p>
                  </motion.div>
                )) : <p className="text-xs text-slate-400 italic">No specific tips generated.</p>}
              </div>
            </div>

            {/* Quick Stats or Info */}
            <div className="bg-slate-900 rounded-3xl p-6 text-white flex flex-col justify-center relative overflow-hidden">
               <div className="absolute top-0 right-0 p-8 opacity-10">
                  <Brain className="w-24 h-24" />
               </div>
               <p className="text-indigo-400 font-bold text-xs uppercase tracking-tighter mb-4">Preparation Scope</p>
               <div className="space-y-4 relative z-10">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400 text-xs font-medium">Technical Depth</span>
                    <span className="text-white font-bold text-xs uppercase bg-indigo-600 px-2 py-0.5 rounded">High</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400 text-xs font-medium">Behavioral Focus</span>
                    <span className="text-white font-bold text-xs uppercase bg-indigo-600 px-2 py-0.5 rounded">Strategic</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400 text-xs font-medium">Complexity</span>
                    <span className="text-white font-bold text-xs uppercase bg-indigo-600 px-2 py-0.5 rounded">Level 4</span>
                  </div>
               </div>
            </div>
          </div>

          {/* Questions Sections */}
          <div className="space-y-8 pt-4 border-t border-slate-100">
            {techQs.length > 0 && (
              <PrepSection 
                title="Technical Excellence" 
                subtitle="Skills & Implementations"
                icon={<Brain className="w-5 h-5 text-indigo-600" />} 
                questions={techQs}
              />
            )}
            
            {behavioralQs.length > 0 && (
              <PrepSection 
                title="Behavioral Alignment" 
                subtitle="Culture & Soft Skills"
                icon={<MessageSquare className="w-5 h-5 text-indigo-600" />} 
                questions={behavioralQs}
              />
            )}

            {situationalQs.length > 0 && (
              <PrepSection 
                title="Situational Awareness" 
                subtitle="Scenario Based Challenges"
                icon={<Rocket className="w-5 h-5 text-indigo-600" />} 
                questions={situationalQs}
              />
            )}
          </div>
        </div>
      </div>
    </motion.div>
  )
}

function PrepSection({ title, subtitle, icon, questions }: { title: string; subtitle: string; icon: React.ReactNode; questions: { question: string; context: string }[] }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3 mb-2">
        <div className="p-2.5 rounded-xl bg-indigo-50 border border-indigo-100">
          {icon}
        </div>
        <div>
          <h4 className="text-slate-900 font-black text-base leading-none mb-1 tracking-tight">{title}</h4>
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">{subtitle}</p>
        </div>
      </div>
      <div className="grid grid-cols-1 gap-3">
        {questions.map((q, i) => (
          <QuestionCard key={i} question={q.question} context={q.context} index={i} />
        ))}
      </div>
    </div>
  )
}

function LoadingProgress({ label, progress }: { label: string; progress: number }) {
  return (
    <div className="space-y-1.5 text-left">
      <div className="flex justify-between text-[10px] font-bold text-slate-400 uppercase tracking-tighter">
        <span>{label}</span>
        <span>{progress}%</span>
      </div>
      <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
        <motion.div 
          className="h-full bg-indigo-600"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 2, repeat: Infinity, repeatType: "reverse" }}
        />
      </div>
    </div>
  )
}

export default App

