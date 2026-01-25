import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Info, ChevronDown, ChevronUp } from 'lucide-react';

export default function QuestionCard({ question, context, index }: { question: string; context: string; index: number }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="group bg-white border border-slate-100 rounded-2xl overflow-hidden hover:border-indigo-200 hover:shadow-md transition-all cursor-pointer shadow-sm"
      onClick={() => setIsOpen(!isOpen)}
    >
      <div className="p-4 flex items-start justify-between gap-4">
        <div className="flex gap-4">
          <span className="flex-shrink-0 w-6 h-6 rounded-full bg-slate-50 border border-slate-200 text-[10px] font-bold flex items-center justify-center text-slate-400 group-hover:text-indigo-600 group-hover:border-indigo-100 transition-colors">
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
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 flex gap-3 shadow-sm">
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
  );
}
