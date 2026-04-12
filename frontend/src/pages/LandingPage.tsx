import { motion } from "framer-motion";
import { ArrowRight, CheckCircle2, ShieldCheck, Sparkles, Users, Workflow } from "lucide-react";
import { Link } from "react-router-dom";
import { usePageMeta } from "../hooks/usePageMeta";
import { SurfaceCard } from "../components/ui/SurfaceCard";
import landingReference from "../assets/templates/landing-reference.png";
import architectureReference from "../assets/templates/product-architecture-reference.png";

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

export default function LandingPage() {
  usePageMeta(
    "Intervux AI | Enterprise Hiring Intelligence Platform",
    "Intervux AI is the AI-powered enterprise hiring intelligence operating system for recruiters, admins, and talent leaders."
  );

  return (
    <div className="bg-slate-100 text-slate-900">
      <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/85 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 md:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-500 text-white">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <p className="font-semibold">Intervux AI</p>
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Hiring Intelligence OS</p>
            </div>
          </div>

          <nav className="hidden items-center gap-6 text-sm font-medium text-slate-600 md:flex">
            <button onClick={() => document.getElementById("workflow")?.scrollIntoView({ behavior: "smooth" })} className="hover:text-blue-700">Workflow</button>
            <button onClick={() => document.getElementById("platform")?.scrollIntoView({ behavior: "smooth" })} className="hover:text-blue-700">Platform</button>
            <button onClick={() => document.getElementById("pricing")?.scrollIntoView({ behavior: "smooth" })} className="hover:text-blue-700">Pricing</button>
          </nav>

          <div className="flex items-center gap-2">
            <Link to="/login" className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700">Sign in</Link>
            <Link to="/signup" className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700">Start trial</Link>
          </div>
        </div>
      </header>

      <section className="mx-auto grid max-w-7xl gap-8 px-4 pb-14 pt-14 md:grid-cols-2 md:px-8">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45 }}>
          <p className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-blue-700">
            <ShieldCheck className="h-3.5 w-3.5" />
            Enterprise-grade AI Recruiting
          </p>
          <h1 className="mt-5 text-4xl font-semibold leading-tight tracking-tight md:text-5xl">
            Build a high-trust
            <span className="text-blue-700"> hiring intelligence command center</span>
          </h1>
          <p className="mt-4 max-w-xl text-lg text-slate-600">
            Intervux AI connects candidate interviews, recruiter workflows, and governance analytics into one premium intelligence layer.
          </p>

          <div className="mt-8 flex flex-wrap gap-3">
            <Link to="/signup" className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-700">
              Launch workspace
              <ArrowRight className="h-4 w-4" />
            </Link>
            <button onClick={() => document.getElementById("platform")?.scrollIntoView({ behavior: "smooth" })} className="rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700">Explore product</button>
          </div>

          <div className="mt-8 grid gap-3 sm:grid-cols-3">
            {trustStats.map((stat) => (
              <SurfaceCard key={stat.label} className="p-4">
                <p className="text-2xl font-semibold text-slate-900">{stat.value}</p>
                <p className="text-sm text-slate-500">{stat.label}</p>
              </SurfaceCard>
            ))}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: 0.1 }}
          className="relative"
        >
          <div className="absolute -left-10 top-12 h-28 w-28 rounded-full bg-blue-200/50 blur-2xl" />
          <SurfaceCard className="relative overflow-hidden p-0">
            <div className="border-b border-slate-200 bg-slate-50 px-5 py-3 text-sm font-semibold text-slate-700">AI Insights Preview</div>
            <div className="p-4">
              <img src={landingReference} alt="Intervux AI premium enterprise landing reference" className="w-full rounded-2xl border border-slate-200 object-cover shadow-sm" />
            </div>
          </SurfaceCard>
        </motion.div>
      </section>

      <section id="workflow" className="mx-auto max-w-7xl px-4 py-10 md:px-8">
        <div className="grid gap-4 md:grid-cols-4">
          {workflowSteps.map((step, index) => (
            <SurfaceCard key={step} title={`Step ${index + 1}`} className="h-full">
              <p className="text-sm text-slate-600">{step}</p>
            </SurfaceCard>
          ))}
        </div>
      </section>

      <section id="platform" className="mx-auto max-w-7xl px-4 py-10 md:px-8">
        <div className="grid gap-4 lg:grid-cols-3">
          <SurfaceCard title="AI analytics workspace" subtitle="Real-time operational intelligence">
            <div className="space-y-3 text-sm text-slate-600">
              <p className="flex items-center gap-2"><Workflow className="h-4 w-4 text-blue-600" /> Pipeline-aware scoring with trend context.</p>
              <p className="flex items-center gap-2"><Users className="h-4 w-4 text-blue-600" /> Team collaboration across recruiter pods.</p>
              <p className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-blue-600" /> Role-based governance and audit trails.</p>
            </div>
          </SurfaceCard>
          <SurfaceCard title="Team collaboration" subtitle="Shared intelligence for every decision">
            <p className="text-sm text-slate-600">
              Recruiters, hiring managers, and admins collaborate in a single workspace with contextual notes, AI recommendations, and decision confidence narratives.
            </p>
          </SurfaceCard>
          <SurfaceCard title="Enterprise controls" subtitle="Secure and compliant by design">
            <p className="text-sm text-slate-600">
              RBAC policies, model confidence monitoring, scoring drift alerts, and deployment guardrails for mission-critical hiring operations.
            </p>
          </SurfaceCard>
        </div>
        <SurfaceCard className="mt-4 p-4" title="Product Architecture Preview" subtitle="Template-aligned visual direction from website template assets">
          <img src={architectureReference} alt="Product architecture overview template" className="w-full rounded-2xl border border-slate-200 object-cover" />
        </SurfaceCard>
      </section>

      <section id="pricing" className="mx-auto max-w-7xl px-4 py-10 md:px-8">
        <div className="grid gap-4 md:grid-cols-3">
          {pricingTiers.map((tier) => (
            <SurfaceCard key={tier.name} title={tier.name} subtitle={tier.description}>
              <p className="text-3xl font-semibold tracking-tight text-slate-900">{tier.price}<span className="text-base font-medium text-slate-500">/mo</span></p>
              <ul className="mt-4 space-y-2 text-sm text-slate-600">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-blue-600" />{feature}</li>
                ))}
              </ul>
            </SurfaceCard>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-12 md:px-8">
        <div className="rounded-[2rem] border border-blue-200 bg-gradient-to-r from-blue-600 to-indigo-600 p-8 text-white shadow-xl">
          <p className="text-xs uppercase tracking-[0.2em] text-blue-100">AI-powered enterprise hiring intelligence operating system</p>
          <h2 className="mt-2 text-3xl font-semibold tracking-tight">Unify recruiting decisions with measurable AI confidence.</h2>
          <Link to="/signup" className="mt-6 inline-flex items-center gap-2 rounded-xl bg-white px-5 py-3 text-sm font-semibold text-blue-700">
            Activate Intervux AI
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>

      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-2 px-4 py-8 text-sm text-slate-500 md:flex-row md:items-center md:justify-between md:px-8">
          <p>© 2026 Intervux AI. Built for intelligent, equitable hiring.</p>
          <p>Security • Compliance • Intelligence</p>
        </div>
      </footer>
    </div>
  );
}

