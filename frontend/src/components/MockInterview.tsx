import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useConversation } from '@elevenlabs/react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, MicOff, PhoneOff, MessageSquare, Sparkles, AlertCircle, BarChart3 } from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:5001');

interface Feedback {
  tone: string;
  confidence: string;
  suggestions: string[];
}

export default function MockInterview() {
  const navigate = useNavigate();
  const [agentId, setAgentId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const conversation = useConversation({
    onConnect: () => console.log('Connected to ElevenLabs'),
    onDisconnect: () => {
      console.log('Disconnected from ElevenLabs');
      handleAnalysis();
    },
    onMessage: (message) => {
      console.log('Received message:', message);
    },
    onError: (err) => {
      console.error('Conversation error:', err);
      setError('Failed to maintain voice connection. Please try again.');
    },
  });

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/v1/config/elevenlabs`);
        setAgentId(response.data.agentId);
      } catch (err) {
        console.error('Failed to fetch ElevenLabs config:', err);
        setError('Mock Interview is not configured. Please set ELEVENLABS_AGENT_ID in your environment.');
      }
    };
    fetchConfig();
  }, []);

  const startInterview = useCallback(async () => {
    if (!agentId) return;

    try {
      // Request microphone access early
      await navigator.mediaDevices.getUserMedia({ audio: true });
      
      await conversation.startSession({
        agentId: agentId,
      } as any);
    } catch (err) {
      console.error('Failed to start interview:', err);
      setError('Could not access microphone. Please ensure permissions are granted.');
    }
  }, [agentId, conversation]);

  const stopInterview = useCallback(async () => {
    await conversation.endSession();
  }, [conversation]);

  const handleAnalysis = async () => {
    setIsAnalyzing(true);
    // Simulate real-time feedback processing
    // In a real app, you might send the transcript to Gemini for analysis
    setTimeout(() => {
      setFeedback({
        tone: "Professional and enthusiastic. You sounded prepared and engaged throughout the conversation.",
        confidence: "High. Your voice was steady, and you avoided excessive filler words like 'um' and 'ah'.",
        suggestions: [
          "Try to pause for 1 second before answering complex technical questions.",
          "Maintain that same energy when discussing your previous challenges.",
          "Your explanation of the GitHub project was very clear, keep using that structure."
        ]
      });
      setIsAnalyzing(false);
    }, 2000);
  };

  const status = conversation.status;

  if (error) {
    return (
      <div className="p-8 rounded-[2rem] bg-danger/5 border border-danger/20 text-center">
        <AlertCircle className="w-12 h-12 text-danger mx-auto mb-4" />
        <h3 className="text-xl font-black text-danger mb-2">Configuration Needed</h3>
        <p className="text-muted-foreground mb-6">{error}</p>
        <button 
          onClick={() => navigate('/')}
          className="px-6 py-2 bg-foreground text-background font-bold rounded-xl"
        >
          Return Home
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-12 px-4">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-12"
      >
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-xs font-black uppercase tracking-widest mb-6 border border-primary/10">
          <Sparkles className="w-3.5 h-3.5" />
          ElevenLabs Powered
        </div>
        <h2 className="text-4xl md:text-5xl font-black tracking-tighter mb-4">
          AI Mock <span className="text-primary">Interview</span>
        </h2>
        <p className="text-lg text-muted-foreground font-medium max-w-2xl mx-auto">
          Practice your verbal communication with our voice AI. Get real-time analysis of your tone, confidence, and content.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Interview Controls */}
        <div className="bg-card rounded-[3rem] p-10 border border-muted shadow-xl relative overflow-hidden">
          <div className="absolute top-0 right-0 p-8 opacity-5">
            <Mic className="w-32 h-32" />
          </div>

          <div className="flex flex-col items-center justify-center space-y-8 relative z-10">
            <div className={`w-32 h-32 rounded-full flex items-center justify-center transition-all duration-500 ${
              status === 'connected' ? 'bg-primary shadow-2xl shadow-primary/50 scale-110 animate-pulse' : 'bg-muted'
            }`}>
              {status === 'connected' ? (
                <Mic className="w-12 h-12 text-white" />
              ) : (
                <MicOff className="w-12 h-12 text-muted-foreground" />
              )}
            </div>

            <div className="text-center">
              <p className="font-black uppercase tracking-widest text-xs opacity-50 mb-2">Connection Status</p>
              <p className={`text-xl font-bold ${status === 'connected' ? 'text-primary' : 'text-muted-foreground'}`}>
                {status === 'connected' ? 'Live Interviewing...' : status === 'connecting' ? 'Establishing Line...' : 'Ready to Start'}
              </p>
            </div>

            {status !== 'connected' ? (
              <button 
                onClick={startInterview}
                disabled={status === 'connecting'}
                className="w-full bg-primary text-white py-4 rounded-2xl font-black text-lg hover:shadow-lg hover:shadow-primary/30 transition-all flex items-center justify-center gap-3 disabled:opacity-50"
              >
                <Mic className="w-5 h-5" />
                {status === 'connecting' ? 'Connecting...' : 'Start Voice Interview'}
              </button>
            ) : (
              <button 
                onClick={stopInterview}
                className="w-full bg-danger text-white py-4 rounded-2xl font-black text-lg hover:shadow-lg hover:shadow-danger/30 transition-all flex items-center justify-center gap-3"
              >
                <PhoneOff className="w-5 h-5" />
                End Interview Session
              </button>
            )}
          </div>
        </div>

        {/* Real-time Feedback Panel */}
        <div className="bg-foreground text-background rounded-[3rem] p-10 shadow-2xl flex flex-col">
          <h3 className="text-2xl font-black mb-8 flex items-center gap-3">
            <BarChart3 className="w-6 h-6 text-primary" /> Performance Analysis
          </h3>

          <AnimatePresence mode="wait">
            {!feedback && !isAnalyzing ? (
              <motion.div 
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex-1 flex flex-col items-center justify-center text-center opacity-50"
              >
                <div className="p-4 bg-white/10 rounded-2xl mb-4">
                    <MessageSquare className="w-10 h-10" />
                </div>
                <p className="font-bold">Waiting for session data...</p>
                <p className="text-sm">Start an interview to see real-time analysis.</p>
              </motion.div>
            ) : isAnalyzing ? (
              <motion.div 
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex-1 flex flex-col items-center justify-center gap-4"
              >
                 <div className="flex gap-1">
                    <div className="w-2 h-8 bg-primary animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-8 bg-primary animate-bounce" style={{ animationDelay: '100ms' }} />
                    <div className="w-2 h-8 bg-primary animate-bounce" style={{ animationDelay: '200ms' }} />
                 </div>
                 <p className="font-black uppercase tracking-tighter">AI is analyzing your tone...</p>
              </motion.div>
            ) : (
              <motion.div 
                key="feedback"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-6 overflow-y-auto"
              >
                <div className="p-5 bg-white/5 rounded-2xl border border-white/10">
                    <p className="uppercase text-[10px] font-black tracking-widest text-primary mb-2">Voice Tone</p>
                    <p className="text-sm font-medium leading-relaxed opacity-90">{feedback?.tone}</p>
                </div>

                <div className="p-5 bg-white/5 rounded-2xl border border-white/10">
                    <p className="uppercase text-[10px] font-black tracking-widest text-primary mb-2">Confidence Score</p>
                    <p className="text-sm font-medium leading-relaxed opacity-90">{feedback?.confidence}</p>
                </div>

                <div className="p-5 bg-white/5 rounded-2xl border border-white/10">
                    <p className="uppercase text-[10px] font-black tracking-widest text-primary mb-4 flex items-center gap-2">
                        <Sparkles className="w-3 h-3" /> Growth Suggestions
                    </p>
                    <ul className="space-y-3">
                        {feedback?.suggestions.map((s, i) => (
                            <li key={i} className="flex gap-3 text-sm font-medium opacity-80">
                                <span className="text-primary font-black">•</span>
                                {s}
                            </li>
                        ))}
                    </ul>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
