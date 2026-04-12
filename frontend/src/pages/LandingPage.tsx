import { motion } from "framer-motion";
import { ArrowRight, CheckCircle2, ShieldCheck, Sparkles, Users, Workflow } from "lucide-react";
import { Link } from "react-router-dom";
import { usePageMeta } from "../hooks/usePageMeta";
import { SurfaceCard } from "../components/ui/SurfaceCard";

const trustStats = [
  { label: "Enterprise teams", value: "240+" },
  { label: "Interviews processed", value: "1.2M" },
  { label: "Decision confidence", value: "97.4%" },
];

const workflowSteps = [
  "Intake role rubric and competency schema",
  "AI interview orchestration and scoring",
  "Recruiter alignment and confidence checks",
  "Decision intelligence with auditability",
];

const pricingTiers = [
  { name: "Growth", price: "$299", description: "For scaling teams", features: ["3 recruiter seats", "AI scorecards", "Core analytics"] },
  { name: "Enterprise", price: "$999", description: "For hiring operations", features: ["Unlimited seats", "RBAC + SSO", "Drift and bias analytics"] },
  { name: "Strategic", price: "Custom", description: "For global orgs", features: ["Dedicated workspace", "Model governance", "Priority support"] },
];

function MockupBar({ width, delay }: { width: string; delay: number }) {
  return (
    <motion.div
      initial={{ scaleX: 0.3, opacity: 0.5 }}
      animate={{ scaleX: 1, opacity: 1 }}
      transition={{ repeat: Infinity, duration: 1.4, delay, repeatType: "reverse" }}
      className="h-2 origin-left rounded-full bg-gradient-to-r from-[#004ac6] to-[#2563eb]"
      style={{ width }}
    />
  );
}

export default function LandingPage() {
  usePageMeta(
    "Intervux AI | Enterprise Hiring Intelligence Platform",
    "Intervux AI is the AI-powered enterprise hiring intelligence operating system for recruiters, admins, and talent leaders."
  );

  return (
    <div className="bg-[#f7f9fb] text-slate-900">
      <header className="sticky top-0 z-40 bg-white/70 backdrop-blur-2xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 md:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-[#004ac6] to-[#2563eb] text-white">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <p className="font-[Manrope] text-lg font-bold">Intervux AI</p>
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Hiring Intelligence OS</p>
            </div>
          </div>

          <nav className="hidden items-center gap-6 text-sm font-medium text-slate-600 md:flex">
            <button onClick={() => document.getElementById("workflow")?.scrollIntoView({ behavior: "smooth" })} className="hover:text-[#004ac6]">Workflow</button>
            <button onClick={() => document.getElementById("platform")?.scrollIntoView({ behavior: "smooth" })} className="hover:text-[#004ac6]">Platform</button>
            <button onClick={() => document.getElementById("pricing")?.scrollIntoView({ behavior: "smooth" })} className="hover:text-[#004ac6]">Pricing</button>
          </nav>

          <div className="flex items-center gap-2">
            <Link to="/login" className="rounded-xl bg-white px-4 py-2 text-sm font-semibold text-slate-700">Sign in</Link>
            <Link to="/signup" className="rounded-xl bg-[#004ac6] px-4 py-2 text-sm font-semibold text-white transition hover:bg-[#003ea8]">Start trial</Link>
          </div>
        </div>
      </header>

      <section className="mx-auto grid max-w-7xl gap-8 px-4 pb-14 pt-14 md:grid-cols-2 md:px-8">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45 }}>
          <p className="inline-flex items-center gap-2 rounded-full bg-[#dbe1ff] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[#003ea8]">
            <ShieldCheck className="h-3.5 w-3.5" />
            Enterprise-grade AI Recruiting
          </p>
          <h1 className="mt-5 font-[Manrope] text-4xl font-bold leading-tight tracking-tight md:text-6xl">
            The intelligence layer for
            <span className="text-[#004ac6]"> high-trust hiring decisions</span>
          </h1>
          <p className="mt-4 max-w-xl text-lg text-slate-600">
            Intervux AI transforms candidate interviews, recruiter operations, and governance controls into one premium command center.
          </p>

          <div className="mt-8 flex flex-wrap gap-3">
            <Link to="/signup" className="inline-flex items-center gap-2 rounded-xl bg-[#004ac6] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#003ea8]">
              Launch workspace
              <ArrowRight className="h-4 w-4" />
            </Link>
            <button onClick={() => document.getElementById("platform")?.scrollIntoView({ behavior: "smooth" })} className="rounded-xl bg-white px-5 py-3 text-sm font-semibold text-slate-700">Explore product</button>
          </div>

          <div className="mt-8 grid gap-3 sm:grid-cols-3">
            {trustStats.map((stat) => (
              <SurfaceCard key={stat.label} className="bg-white p-4">
                <p className="font-[Manrope] text-2xl font-bold text-slate-900">{stat.value}</p>
                <p className="text-sm text-slate-500">{stat.label}</p>
              </SurfaceCard>
            ))}
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45, delay: 0.1 }}>
          <SurfaceCard className="bg-white p-0">
            <div className="bg-[#f2f4f6] px-5 py-3 text-sm font-semibold text-slate-700">Live AI Product Mockup</div>
            <div className="grid gap-4 p-5">
              <div className="rounded-2xl bg-[#f7f9fb] p-4">
                <p className="text-xs uppercase tracking-[0.14em] text-slate-500">Candidate confidence model</p>
                <p className="mt-2 font-[Manrope] text-3xl font-bold text-[#004ac6]">91.2%</p>
                <div className="mt-4 space-y-2">
                  <MockupBar width="92%" delay={0} />
                  <MockupBar width="68%" delay={0.2} />
                  <MockupBar width="84%" delay={0.4} />
                </div>
              </div>
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="rounded-2xl bg-[#f2f4f6] p-4">
                  <p className="text-xs uppercase tracking-[0.12em] text-slate-500">Decision SLA</p>
                  <p className="mt-1 font-[Manrope] text-2xl font-bold">18 hrs</p>
                </div>
                <div className="rounded-2xl bg-[#f2f4f6] p-4">
                  <p className="text-xs uppercase tracking-[0.12em] text-slate-500">Recruiter alignment</p>
                  <p className="mt-1 font-[Manrope] text-2xl font-bold">94%</p>
                </div>
              </div>
            </div>
          </SurfaceCard>
        </motion.div>
      </section>

      <section id="workflow" className="mx-auto max-w-7xl px-4 py-10 md:px-8">
        <div className="grid gap-4 md:grid-cols-4">
          {workflowSteps.map((step, index) => (
            <SurfaceCard key={step} title={`Step ${index + 1}`} className="h-full bg-white">
              <p className="text-sm text-slate-600">{step}</p>
            </SurfaceCard>
          ))}
        </div>
      </section>

      <section id="platform" className="mx-auto max-w-7xl px-4 py-10 md:px-8">
        <div className="grid gap-4 lg:grid-cols-3">
          <SurfaceCard title="AI analytics workspace" subtitle="Real-time operational intelligence">
            <div className="space-y-3 text-sm text-slate-600">
              <p className="flex items-center gap-2"><Workflow className="h-4 w-4 text-[#004ac6]" />Pipeline-aware scoring with trend context.</p>
              <p className="flex items-center gap-2"><Users className="h-4 w-4 text-[#004ac6]" />Team collaboration across recruiter pods.</p>
              <p className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-[#004ac6]" />Role-based governance and audit trails.</p>
            </div>
          </SurfaceCard>
          <SurfaceCard title="Team collaboration" subtitle="Shared intelligence for every decision">
            <p className="text-sm text-slate-600">Recruiters, hiring managers, and admins collaborate with contextual notes, AI recommendations, and confidence narratives.</p>
          </SurfaceCard>
          <SurfaceCard title="Enterprise controls" subtitle="Secure and compliant by design">
            <p className="text-sm text-slate-600">RBAC policies, model confidence monitoring, scoring drift alerts, and deployment guardrails for mission-critical operations.</p>
          </SurfaceCard>
        </div>
      </section>

      <section id="pricing" className="mx-auto max-w-7xl px-4 py-10 md:px-8">
        <div className="grid gap-4 md:grid-cols-3">
          {pricingTiers.map((tier) => (
            <SurfaceCard key={tier.name} title={tier.name} subtitle={tier.description}>
              <p className="font-[Manrope] text-3xl font-bold tracking-tight text-slate-900">{tier.price}<span className="text-base font-medium text-slate-500">/mo</span></p>
              <ul className="mt-4 space-y-2 text-sm text-slate-600">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-[#004ac6]" />{feature}</li>
                ))}
              </ul>
            </SurfaceCard>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-12 md:px-8">
        <div className="rounded-[2rem] bg-gradient-to-r from-[#004ac6] to-[#2563eb] p-8 text-white shadow-xl">
          <p className="text-xs uppercase tracking-[0.2em] text-blue-100">AI-powered enterprise hiring intelligence operating system</p>
          <h2 className="mt-2 font-[Manrope] text-3xl font-bold tracking-tight">Unify recruiting decisions with measurable AI confidence.</h2>
          <Link to="/signup" className="mt-6 inline-flex items-center gap-2 rounded-xl bg-white px-5 py-3 text-sm font-semibold text-[#004ac6]">
            Activate Intervux AI
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>

      <footer className="bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-2 px-4 py-8 text-sm text-slate-500 md:flex-row md:items-center md:justify-between md:px-8">
          <p>© 2026 Intervux AI. Built for intelligent, equitable hiring.</p>
          <p>Security • Compliance • Intelligence</p>
        </div>
      </footer>
    </div>
  );
}
