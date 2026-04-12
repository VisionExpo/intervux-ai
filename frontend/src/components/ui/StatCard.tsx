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
    <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-[0_12px_24px_-18px_rgba(15,23,42,0.45)] transition-all duration-200 hover:-translate-y-1 hover:shadow-[0_20px_38px_-20px_rgba(30,64,175,0.35)]">
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-semibold tracking-tight text-slate-900">{value}</p>
      <p className={`mt-3 inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold ${positive ? "bg-blue-50 text-blue-700" : "bg-rose-50 text-rose-700"}`}>
        {positive ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}
        {change}
      </p>
    </div>
  );
}

