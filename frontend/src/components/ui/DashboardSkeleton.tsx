export function DashboardSkeleton() {
  return (
    <div className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="h-32 animate-pulse rounded-3xl border border-slate-200 bg-white" />
        ))}
      </div>
      <div className="grid gap-4 xl:grid-cols-3">
        <div className="h-72 animate-pulse rounded-3xl border border-slate-200 bg-white xl:col-span-2" />
        <div className="h-72 animate-pulse rounded-3xl border border-slate-200 bg-white" />
      </div>
    </div>
  );
}

