import { motion } from "framer-motion";
import { Sparkles, ShieldCheck, Zap } from "lucide-react";
import styles from "./LoadingScreen.module.css";

export function LoadingScreen() {
  return (
    <div className={styles.container}>
      <div className={styles.bgGlow} />
      
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className={styles.content}
      >
        <div className={styles.iconWrapper}>
          <motion.div
            animate={{ 
              rotate: 360,
              boxShadow: [
                "0 0 20px rgba(14, 165, 233, 0.2)",
                "0 0 50px rgba(14, 165, 233, 0.4)",
                "0 0 20px rgba(14, 165, 233, 0.2)"
              ]
            }}
            transition={{ rotate: { duration: 4, repeat: Infinity, ease: "linear" }, boxShadow: { duration: 2, repeat: Infinity } }}
            className={styles.glowCircle}
          />
          <Sparkles className={styles.icon} size={32} />
        </div>

        <h2 className={styles.title}>Intervux AI</h2>
        <div className={styles.progressContainer}>
          <motion.div 
            initial={{ width: "0%" }}
            animate={{ width: "100%" }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            className={styles.progressBar}
          />
        </div>

        <div className={styles.statusRow}>
          <div className={styles.statusItem}>
            <ShieldCheck size={14} className={styles.statusIcon} />
            Secure Session
          </div>
          <div className={styles.statusDivider} />
          <div className={styles.statusItem}>
            <Zap size={14} className={styles.statusIcon} />
            AI Ready
          </div>
        </div>
        
        <p className={styles.subtitle}>Initializing intelligence workspace...</p>
      </motion.div>
    </div>
  );
}
