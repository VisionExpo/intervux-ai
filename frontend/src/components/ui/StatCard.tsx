import { ArrowUpRight, ArrowDownRight } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string;
  change: string;
  trend?: "up" | "down";
}

export function StatCard({ label, value, change, trend = "up" }: StatCardProps) {
  const positive = trend === "up";

  return (
    <div className="rounded-3xl bg-white p-5 shadow-[0_24px_44px_-36px_rgba(15,23,42,0.42)] transition-all duration-200 hover:-translate-y-1 hover:shadow-[0_32px_54px_-32px_rgba(37,99,235,0.35)]">
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">{label}</p>
      <p className="mt-3 font-[Manrope] text-4xl font-bold tracking-tight text-slate-900">{value}</p>
      <p className={`mt-3 inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold ${positive ? "bg-blue-100 text-blue-700" : "bg-amber-100 text-amber-700"}`}>
        {positive ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}
        {change}
      </p>
    </div>
  );
}
