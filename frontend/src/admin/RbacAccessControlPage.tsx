import { useState } from "react";
import { motion } from "framer-motion";
import { ShieldAlert, ShieldCheck, Users } from "lucide-react";
import { SurfaceCard } from "../components/ui/SurfaceCard";
import { usePageMeta } from "../hooks/usePageMeta";

export default function RbacAccessControlPage() {
  const [selectedRole, setSelectedRole] = useState("Recruiter");

  usePageMeta("RBAC and Access Control | Intervux AI", "Enterprise-grade role access control with user directory, permission matrix, audit logs, and security health.");

  return (
    <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
      <section className="rounded-[2rem] bg-white px-6 py-6 shadow-sm">
        <p className="text-sm text-slate-500">Role Access Control</p>
        <h1 className="mt-1 font-[Manrope] text-3xl font-bold tracking-tight text-slate-900">Enterprise identity and permission intelligence</h1>
      </section>

      <div className="grid gap-4 xl:grid-cols-3">
        <SurfaceCard title="Active user directory" subtitle="Current platform users" className="xl:col-span-2">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[540px] text-left text-sm">
              <thead>
                <tr className="text-slate-500">
                  <th className="pb-2 font-medium">User</th>
                  <th className="pb-2 font-medium">Role</th>
                  <th className="pb-2 font-medium">Status</th>
                  <th className="pb-2 font-medium">Last Activity</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["Priya Menon", "Admin", "Active", "2m ago"],
                  ["Aman Jain", "Recruiter", "Active", "5m ago"],
                  ["Riya Kapoor", "Recruiter", "Restricted", "1h ago"],
                  ["Megan Scott", "Candidate", "Active", "3h ago"],
                ].map(([name, role, status, time]) => (
                  <tr key={name} className="even:bg-[#f7f9fb]">
                    <td className="py-3 font-semibold text-slate-900">{name}</td>
                    <td className="py-3 text-slate-600">{role}</td>
                    <td className="py-3"><span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${status === "Active" ? "bg-[#dbe1ff] text-[#003ea8]" : "bg-[#ffdbcd] text-[#7d2d00]"}`}>{status}</span></td>
                    <td className="py-3 text-slate-600">{time}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </SurfaceCard>

        <SurfaceCard title="Security health" subtitle="Access policy posture">
          <div className="space-y-3 text-sm text-slate-600">
            <p className="rounded-2xl bg-[#dbe1ff] p-3 text-[#003ea8]"><ShieldCheck className="mr-2 inline h-4 w-4" />MFA adoption 98.2%</p>
            <p className="rounded-2xl bg-[#ffdbcd] p-3 text-[#7d2d00]"><ShieldAlert className="mr-2 inline h-4 w-4" />3 stale roles need review</p>
            <p className="rounded-2xl bg-[#dbe1ff] p-3 text-[#003ea8]"><Users className="mr-2 inline h-4 w-4" />9 smart role suggestions pending</p>
          </div>
        </SurfaceCard>
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <SurfaceCard title="Permission matrix" subtitle="Role capabilities and access scope" className="xl:col-span-2" action={<select value={selectedRole} onChange={(e) => setSelectedRole(e.target.value)} className="rounded-xl bg-[#f2f4f6] px-2 py-1 text-xs font-semibold text-slate-700"><option>Recruiter</option><option>Admin</option><option>Candidate</option></select>}>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[540px] text-sm">
              <thead>
                <tr className="text-slate-500">
                  <th className="pb-2 text-left font-medium">Capability</th>
                  <th className="pb-2 text-center font-medium">Admin</th>
                  <th className="pb-2 text-center font-medium">Recruiter</th>
                  <th className="pb-2 text-center font-medium">Candidate</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["View analytics", "Yes", "Yes", "No"],
                  ["Edit scoring models", "Yes", "No", "No"],
                  ["Manage candidates", "Yes", "Yes", "Limited"],
                  ["Access interview reports", "Yes", "Yes", "Own"],
                ].map(([permission, admin, recruiter, candidate]) => (
                  <tr key={permission} className="even:bg-[#f7f9fb] text-slate-700">
                    <td className="py-3 font-medium">{permission}</td>
                    <td className={`py-3 text-center ${selectedRole === "Admin" ? "font-semibold text-[#004ac6]" : ""}`}>{admin}</td>
                    <td className={`py-3 text-center ${selectedRole === "Recruiter" ? "font-semibold text-[#004ac6]" : ""}`}>{recruiter}</td>
                    <td className={`py-3 text-center ${selectedRole === "Candidate" ? "font-semibold text-[#004ac6]" : ""}`}>{candidate}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </SurfaceCard>

        <SurfaceCard title="Audit logs" subtitle="RBAC event history">
          <ul className="space-y-2 text-sm text-slate-600">
            <li className="rounded-2xl bg-[#f2f4f6] p-3">Role escalation approved for Aman Jain.</li>
            <li className="rounded-2xl bg-[#f2f4f6] p-3">Permissions rollback completed for Team Gamma.</li>
            <li className="rounded-2xl bg-[#f2f4f6] p-3">Security review exported for compliance cycle.</li>
          </ul>
          <button className="mt-4 w-full rounded-xl bg-[#004ac6] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[#003ea8]">Deploy access policy changes</button>
        </SurfaceCard>
      </div>
    </motion.div>
  );
}
