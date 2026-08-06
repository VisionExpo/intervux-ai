import { motion } from "framer-motion";
import { ArrowRight, CheckCircle2, ShieldCheck, Sparkles, Workflow, Users, LayoutDashboard, Activity, Terminal } from "lucide-react";
import { Link } from "react-router-dom";
import { usePageMeta } from "../hooks/usePageMeta";
import styles from "./LandingPage.module.css";

const pricingTiers = [
  { name: "Growth", price: "$299", description: "For scaling teams", features: ["3 recruiter seats", "AI scorecards", "Core analytics"] },
  { name: "Enterprise", price: "$999", description: "For hiring operations", features: ["Unlimited seats", "RBAC + SSO", "Drift and bias analytics"] },
  { name: "Strategic", price: "Custom", description: "For global orgs", features: ["Dedicated workspace", "Model governance", "Priority support"] },
];

export default function LandingPage() {
  usePageMeta(
    "Intervux AI | Enterprise Hiring Intelligence Platform",
    "Intervux AI is the AI-powered enterprise hiring intelligence operating system for recruiters, admins, and talent leaders."
  );

  return (
    <div className={styles.landingRoot}>
      {/* Animated Background Elements */}
      <div className={styles.bgGradient} />
      <div className={styles.bgOrbs} />
      <div className={styles.bgOrbs2} />

      {/* Glossy Navigation */}
      <header className={styles.header}>
        <div className={styles.logo}>
          <div className={styles.logoIcon}>
            <Sparkles size={20} color="#fff" />
          </div>
          <span style={{ color: "var(--text-primary)" }}>Intervux AI</span>
        </div>

        <nav className={styles.navLinks}>
          <button onClick={() => document.getElementById("workflow")?.scrollIntoView({ behavior: "smooth" })}>Workflow</button>
          <button onClick={() => document.getElementById("platform")?.scrollIntoView({ behavior: "smooth" })}>Platform</button>
          <button onClick={() => document.getElementById("pricing")?.scrollIntoView({ behavior: "smooth" })}>Pricing</button>
        </nav>

        <div className={styles.authActions}>
          <Link to="/login" className={styles.signInBtn}>Sign in</Link>
          <Link to="/signup" className={styles.startTrialBtn}>Start trial</Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className={styles.heroSection}>
        <motion.div 
          className={styles.fadeUp} 
          initial={{ opacity: 0, y: 20 }} 
          animate={{ opacity: 1, y: 0 }} 
          transition={{ duration: 0.6 }}
        >
          <div className={styles.heroBadge}>
            <ShieldCheck size={14} />
            Enterprise-grade AI Recruiting
          </div>
          
          <h1 className={styles.heroTitle}>
            The intelligence layer for
            <br />
            <span className={styles.heroTitleHighlight}>high-trust hiring decisions</span>
          </h1>

          <p className={styles.heroSubtitle}>
            Intervux AI transforms candidate interviews, recruiter operations, and governance controls into one premium command center with guaranteed deterministic outcomes.
          </p>

          <div className={styles.heroCta}>
            <Link to="/dashboard-preview" className={styles.primaryCta}>
              Experience AI Interview
              <ArrowRight size={18} />
            </Link>
            <button 
              onClick={() => document.getElementById("platform")?.scrollIntoView({ behavior: "smooth" })} 
              className={styles.secondaryCta}
            >
              Explore product
            </button>
          </div>
        </motion.div>

        {/* Interactive Simulated UI Mockup */}
        <motion.div 
          className={`${styles.mockupContainer} ${styles.fadeUp}`}
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <div className={styles.mockupWindow}>
            <div className={styles.mockupHeader}>
              <div className={`${styles.macDot} ${styles.red}`} />
              <div className={`${styles.macDot} ${styles.yellow}`} />
              <div className={`${styles.macDot} ${styles.green}`} />
              <div style={{ marginLeft: "1rem", fontSize: "0.75rem", color: "var(--text-secondary)"}}>intervux-ai-dashboard</div>
            </div>
            
            <div className={styles.mockupBody}>
              <div className={styles.mockupSidebar}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "2rem", color: "var(--text-primary)", fontWeight: 600 }}>
                  <LayoutDashboard size={18} color="var(--accent-primary)"/> Dashboard
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1rem", color: "var(--text-secondary)" }}>
                  <Users size={16} /> Active Pipelines
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1rem", color: "var(--text-secondary)" }}>
                  <Terminal size={16} /> Technical Review
                </div>
              </div>

              <div className={styles.mockupContent}>
                <div style={{ display: "flex", gap: "1rem" }}>
                  <div className={styles.mockCard} style={{ flex: 1 }}>
                    <div className={styles.cardDesc}>Candidate Confidence Model</div>
                    <div className={styles.scoreDisplay}>
                      <span className={styles.scoreValue}>91.2<span style={{ fontSize: "1.5rem" }}>%</span></span>
                    </div>
                  </div>
                  <div className={styles.mockCard} style={{ flex: 1 }}>
                    <div className={styles.cardDesc}>Decision SLA</div>
                    <div className={styles.scoreDisplay}>
                      <span className={styles.scoreValue}>18<span style={{ fontSize: "1.5rem", color: "var(--text-secondary)"}}> hrs</span></span>
                    </div>
                  </div>
                </div>

                <div className={styles.mockCard}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "1rem" }}>
                    <div style={{ color: "var(--text-primary)", fontWeight: 600 }}>Real-time Interview Feed</div>
                    <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", fontSize: "0.75rem", color: "var(--text-secondary)"}}>
                      <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#10b981" }} />
                      Actively analyzing
                    </div>
                  </div>
                  <div className={styles.mockSkeletonText} style={{ width: "80%" }} />
                  <div className={styles.mockSkeletonText} style={{ width: "90%" }} />
                  <div className={styles.mockSkeletonText} style={{ width: "60%" }} />
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* Platform Features - Bento Grid */}
      <section id="platform" className={styles.featuresSection}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>Built for intelligence and scale</h2>
          <p style={{ color: "var(--text-secondary)" }}>Mission-critical recruitment infrastructure that doesn't compromise on design or data security.</p>
        </div>

        <div className={styles.bentoGrid}>
          <div className={`${styles.bentoCard} ${styles.bentoLarge}`}>
            <div className={styles.cardIcon}>
              <Activity size={24} />
            </div>
            <h3 className={styles.cardTitle}>Real-Time Evaluation Engine</h3>
            <p className={styles.cardDesc}>
              Intervux AI captures thousands of non-verbal and verbal data points during the session, computing an algorithmic health score mapped strictly to your core competencies. This removes interviewer bias and ensures a mathematical baseline of candidate quality.
            </p>
          </div>

          <div className={styles.bentoCard}>
            <div className={styles.cardIcon}>
              <Workflow size={24} />
            </div>
            <h3 className={styles.cardTitle}>Intelligent Orchestration</h3>
            <p className={styles.cardDesc}>Sync seamlessly with ATS to drive dynamic scoring and automated workflows.</p>
          </div>

          <div className={styles.bentoCard}>
            <div className={styles.cardIcon}>
              <Users size={24} />
            </div>
            <h3 className={styles.cardTitle}>Recruiter Collaboration</h3>
            <p className={styles.cardDesc}>Share live, interactive evidence and context-rich AI scorecards to streamline hiring panel consensus.</p>
          </div>

          <div className={styles.bentoCard}>
            <div className={styles.cardIcon}>
              <ShieldCheck size={24} />
            </div>
            <h3 className={styles.cardTitle}>Enterprise Controls</h3>
            <p className={styles.cardDesc}>Rigorous RBAC policies, bias drift alerts, and robust audit trails keep operations compliant.</p>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className={styles.featuresSection} style={{ marginTop: "4rem" }}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>Transparent Enterprise Plans</h2>
        </div>
        <div className={styles.bentoGrid}>
          {pricingTiers.map((tier) => (
            <div key={tier.name} className={styles.bentoCard}>
              <h3 className={styles.cardTitle}>{tier.name}</h3>
              <p className={styles.cardDesc} style={{ marginBottom: "1.5rem" }}>{tier.description}</p>
              <div style={{ fontSize: "2.5rem", fontWeight: 800, color: "var(--text-primary)", marginBottom: "1.5rem" }}>
                {tier.price} <span style={{ fontSize: "1rem", color: "var(--text-secondary)", fontWeight: 500 }}>/mo</span>
              </div>
              <ul style={{ display: "flex", flexDirection: "column", gap: "0.75rem", padding: 0 }}>
                {tier.features.map(feat => (
                  <li key={feat} style={{ display: "flex", gap: "0.5rem", alignItems: "center", color: "var(--text-secondary)", fontSize: "0.875rem" }}>
                    <CheckCircle2 size={16} color="var(--accent-primary)" />
                    {feat}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className={styles.footer}>
        <div>© 2026 Intervux AI. Built for intelligent, equitable hiring.</div>
        <div>Security • Compliance • Intelligence</div>
      </footer>
    </div>
  );
}
