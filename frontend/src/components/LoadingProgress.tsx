import { motion } from 'framer-motion';

export default function LoadingProgress({ label, progress }: { label: string; progress: number }) {
  return (
    <div className="space-y-1.5 text-left">
      <div className="flex justify-between text-[10px] font-bold text-slate-400 uppercase tracking-tighter">
        <span>{label}</span>
        <span>{progress}%</span>
      </div>
      <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden border border-slate-200/50">
        <motion.div 
          className="h-full bg-indigo-600"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 2, repeat: Infinity, repeatType: "reverse" }}
        />
      </div>
    </div>
  );
}
