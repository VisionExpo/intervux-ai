import { motion, AnimatePresence } from "framer-motion";
import { CreditCard, ShieldCheck, Sparkles, X, Zap } from "lucide-react";
import { SurfaceCard } from "./SurfaceCard";

interface CreditUpgradeModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CreditUpgradeModal({ isOpen, onClose }: CreditUpgradeModalProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/60 backdrop-blur-sm">
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="max-w-lg w-full"
          >
            <SurfaceCard className="relative p-8 border-[var(--border-glass)] glass-heavy shadow-2xl">
              <button 
                onClick={onClose}
                className="absolute top-4 right-4 p-2 rounded-full hover:bg-white/10 text-[var(--text-tertiary)]"
              >
                <X size={20} />
              </button>

              <div className="flex flex-col items-center text-center">
                <div className="w-16 h-16 rounded-2xl bg-[var(--accent-indigo-glow)] flex items-center justify-center text-[var(--accent-indigo)] mb-6">
                  <Zap size={32} />
                </div>

                <h2 className="text-3xl font-bold text-[var(--text-primary)] mb-2">Refill Your Credits</h2>
                <p className="text-[var(--text-secondary)] mb-8">
                  You've used all your free practice sessions. Upgrade to Pro for unlimited AI-powered interview intelligence.
                </p>

                <div className="grid grid-cols-1 gap-4 w-full mb-8 text-left">
                  <div className="p-4 rounded-xl bg-[var(--surface-glass-light)] border border-[var(--border-glass)] flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-sky-500/10 flex items-center justify-center text-sky-500">
                      <Sparkles size={20} />
                    </div>
                    <div>
                      <p className="font-bold text-[var(--text-primary)]">unlimited Practice</p>
                      <p className="text-xs text-[var(--text-tertiary)]">Zero limits on AI feedback sessions.</p>
                    </div>
                  </div>
                  <div className="p-4 rounded-xl bg-[var(--surface-glass-light)] border border-[var(--border-glass)] flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-500">
                      <ShieldCheck size={20} />
                    </div>
                    <div>
                      <p className="font-bold text-[var(--text-primary)]">Verified Certificates</p>
                      <p className="text-xs text-[var(--text-tertiary)]">Showcase your skills to top recruiters.</p>
                    </div>
                  </div>
                </div>

                <button className="w-full py-4 bg-[var(--accent-indigo)] text-white rounded-2xl font-bold text-lg shadow-xl shadow-indigo-500/20 transform transition-all hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center gap-2">
                  <CreditCard size={20} />
                  Upgrade to Pro — $29/mo
                </button>
                
                <p className="mt-4 text-xs text-[var(--text-tertiary)]">
                  Secure checkout powered by Stripe. Cancel anytime.
                </p>
              </div>
            </SurfaceCard>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
