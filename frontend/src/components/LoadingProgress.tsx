import { motion } from 'framer-motion';

export default function LoadingProgress({ label, progress }: { label: string; progress: number }) {
  return (
    <div className="space-y-1.5 text-left">
      <div className="flex justify-between text-[10px] font-bold text-muted-foreground uppercase tracking-tighter">
        <span>{label}</span>
        <span>{progress}%</span>
      </div>
      <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden border border-border">
        <motion.div 
          className="h-full bg-primary"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 2, repeat: Infinity, repeatType: "reverse" }}
        />
      </div>
    </div>
  );
}
