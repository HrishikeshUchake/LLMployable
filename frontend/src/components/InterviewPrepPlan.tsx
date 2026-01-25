import { useState } from 'react';
import { motion } from 'framer-motion';
import { Trophy, Check, Copy, Lightbulb, CheckCircle2, Brain, MessageSquare, Briefcase } from 'lucide-react';
import QuestionCard from './QuestionCard';

interface InterviewPrepData {
  tips: string[];
  technical_questions: { question: string; context: string }[];
  behavioral_questions: { question: string; context: string }[];
  situational_questions: { question: string; context: string }[];
  winning_strategy: string;
}

export default function InterviewPrepPlan({ data }: { data: InterviewPrepData }) {
  const [copied, setCopied] = useState(false);

  // Defensive values
  const tips = Array.isArray(data?.tips) ? data.tips : [];
  const techQs = Array.isArray(data?.technical_questions) ? data.technical_questions : [];
  const behavioralQs = Array.isArray(data?.behavioral_questions) ? data.behavioral_questions : [];
  const situationalQs = Array.isArray(data?.situational_questions) ? data.situational_questions : [];
  const winningStrategy = data?.winning_strategy || 'Be prepared and stay confident.';

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
`.trim();

      navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="mt-8 space-y-6"
    >
      <div className="bg-card rounded-[2rem] border border-border shadow-xl overflow-hidden">
        <div className="bg-primary p-6 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Trophy className="w-6 h-6 text-success" />
            <h3 className="text-xl font-black tracking-tight text-white mb-0">Interview Game Plan</h3>
          </div>
          <button 
            type="button"
            onClick={copyToClipboard}
            className="flex items-center gap-2 bg-white/10 hover:bg-white/20 px-4 py-2 rounded-xl transition-all text-sm font-bold border border-white/10"
          >
            {copied ? (
              <><Check className="w-4 h-4 text-success" /> Copied!</>
            ) : (
              <><Copy className="w-4 h-4" /> Copy Plan</>
            )}
          </button>
        </div>
        
        <div className="p-8 space-y-10">
          <div className="relative group">
            <div className="absolute -inset-4 bg-muted/50 rounded-[2rem] -z-10 group-hover:bg-muted transition-colors" />
            <h4 className="text-primary font-bold mb-3 flex items-center gap-2 text-lg">
              <Lightbulb className="w-6 h-6 text-primary" /> Winning Strategy
            </h4>
            <p className="text-primary/80 text-sm leading-relaxed font-semibold italic">
              "{winningStrategy}"
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-4">
              <h4 className="text-foreground font-black text-sm uppercase tracking-widest flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-primary" /> Actionable Tips
              </h4>
              <div className="space-y-3">
                {tips.length > 0 ? tips.map((tip, i) => (
                  <motion.div 
                    key={i} 
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className="flex gap-3 p-4 rounded-2xl bg-muted/30 border border-border items-start hover:border-primary/20 transition-colors"
                  >
                    <div className="mt-1 w-1.5 h-1.5 rounded-full bg-primary shrink-0" />
                    <p className="text-sm text-foreground/70 font-medium leading-relaxed">{tip}</p>
                  </motion.div>
                )) : <p className="text-xs text-muted-foreground italic">No specific tips generated.</p>}
              </div>
            </div>

            <div className="bg-primary rounded-3xl p-6 text-white flex flex-col justify-center relative overflow-hidden">
               <div className="absolute top-0 right-0 p-8 opacity-10">
                  <Brain className="w-24 h-24" />
               </div>
               <p className="text-success font-bold text-xs uppercase tracking-tighter mb-4">Preparation Scope</p>
               <div className="space-y-4 relative z-10">
                  <div className="flex items-center justify-between">
                    <span className="text-white/60 text-xs font-medium">Technical Depth</span>
                    <span className="text-white font-bold text-xs uppercase bg-white/10 px-2 py-0.5 rounded">High</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-white/60 text-xs font-medium">Behavioral Focus</span>
                    <span className="text-white font-bold text-xs uppercase bg-white/10 px-2 py-0.5 rounded">Strategic</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-white/60 text-xs font-medium">Complexity</span>
                    <span className="text-white font-bold text-xs uppercase bg-white/10 px-2 py-0.5 rounded">Level 4</span>
                  </div>
               </div>
            </div>
          </div>

          <div className="space-y-8 pt-4 border-t border-border">
            {techQs.length > 0 && (
              <PrepSection 
                title="Technical Excellence" 
                subtitle="Skills & Implementations"
                icon={<Brain className="w-5 h-5 text-primary" />} 
                questions={techQs}
              />
            )}
            
            {behavioralQs.length > 0 && (
              <PrepSection 
                title="Behavioral Alignment" 
                subtitle="Culture & Soft Skills"
                icon={<MessageSquare className="w-5 h-5 text-primary" />} 
                questions={behavioralQs}
              />
            )}

            {situationalQs.length > 0 && (
              <PrepSection 
                title="Situational Awareness" 
                subtitle="Scenario Based Challenges"
                icon={<Briefcase className="w-5 h-5 text-primary" />} 
                questions={situationalQs}
              />
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function PrepSection({ title, subtitle, icon, questions }: { title: string; subtitle: string; icon: React.ReactNode; questions: { question: string; context: string }[] }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3 mb-2">
        <div className="p-2.5 rounded-xl bg-muted border border-border">
          {icon}
        </div>
        <div>
          <h4 className="text-foreground font-black text-base leading-none mb-1 tracking-tight">{title}</h4>
          <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-[0.2em]">{subtitle}</p>
        </div>
      </div>
      <div className="grid grid-cols-1 gap-3">
        {questions.map((q, i) => (
          <QuestionCard key={i} question={q.question} context={q.context} index={i} />
        ))}
      </div>
    </div>
  );
}
