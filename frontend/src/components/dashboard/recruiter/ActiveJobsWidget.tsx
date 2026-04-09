import React from 'react';
import { DashboardCard } from '../shared/DashboardCard';

export const ActiveJobsWidget: React.FC = () => {
  return (
    <DashboardCard>
      <h3 className="text-lg font-bold font-headline text-slate-900 dark:text-slate-800 mb-6">Active Jobs</h3>
      <div className="space-y-6">
        {/* Job 1 */}
        <div className="group cursor-pointer">
          <div className="flex justify-between items-start mb-2">
            <h4 className="text-sm font-bold text-slate-900 dark:text-slate-800 group-hover:text-primary transition-colors">Senior Product Designer</h4>
            <span className="text-[10px] font-bold text-slate-400">2d ago</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex -space-x-2">
              <img className="w-6 h-6 rounded-full border-2 border-white object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCRT7G5PlI0efNsKyBu6yyRdlCmlW_hvQ78SsXJiu1P95o-swCLTPHErGP556NRKCgMGH5EoVHNCZcabyIAXPQGPjWZuZILuJxwhffqlZycNlqNA0p4MmTzhNsj-t8klLS0xFaA_m2uERXOu4aASxWFWKcPKFaeEpoTTvNImiGU99e50H9UOArQyU5Y06IkasIgM3kxFFThkO3Nns1YruhfTD8fyw7fN2qhO6pj_2_XrAwoGsce4mKaWmDBqOtJACvA2hRJdZLYOTw" alt="candidate" />
              <img className="w-6 h-6 rounded-full border-2 border-white object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuD_7ho-EQRutI5WdTuT845d8FaocdUiJNh96mkCeLVM7Aajg8mlQYeo1yYRB7BdWrVw4WQDbLwkBVjO8InVmgUIyFALADOFUbclr-4X9nB0pSbIWlBPVb3-mMdRucPymK-TDa82LBI0qZjwd9rhiXNa8TeTTZcWy12bfrJAsEvj29zrVlp5SMfyd-rq-8kKH4vnMiVFGpiP36v5gI5iAwuwZ2GwmwllPRfwOFQb5zrb8muhyhrDkWGRdH7M1LCcfs7yF3DMBmSebH8" alt="candidate" />
              <div className="w-6 h-6 rounded-full border-2 border-white bg-slate-100 dark:bg-slate-200 flex items-center justify-center text-[8px] font-bold text-slate-600">+12</div>
            </div>
            <span className="text-[10px] font-bold text-slate-600 bg-slate-100 dark:bg-slate-200 px-2 py-1 rounded">24 Candidates</span>
          </div>
        </div>

        {/* Job 2 */}
        <div className="group cursor-pointer">
          <div className="flex justify-between items-start mb-2">
            <h4 className="text-sm font-bold text-slate-900 dark:text-slate-800 group-hover:text-primary transition-colors">Staff Engineer, Cloud</h4>
            <span className="text-[10px] font-bold text-slate-400">5d ago</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex -space-x-2">
              <img className="w-6 h-6 rounded-full border-2 border-white object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDw8mIW3JRmXuzqv65IM--6hlrQS_dhTQfY6SVy3rXJwNMGBtOHDfNPsPHiB3Fr8lsXGgGppW2WTeb3qAB5F2UG0EvTfiWJTBzcBHjzvaY2lk4YH0tYnLoH2unEIenbFsu9qGvWB9HScAXIlJ8iZFK8feK7zJPFcdL4hMSnVjucuBzu5p65ydIeqZPPxaLwIfOQ2xxG745jBe31V7GaPIX54QJSxB6XJ6nRLuPPXAmJLRC3jiVGnQg1jFuNk8RfLU-nwARYwp1unSk" alt="candidate" />
              <div className="w-6 h-6 rounded-full border-2 border-white bg-slate-100 dark:bg-slate-200 flex items-center justify-center text-[8px] font-bold text-slate-600">+5</div>
            </div>
            <span className="text-[10px] font-bold text-slate-600 bg-slate-100 dark:bg-slate-200 px-2 py-1 rounded">8 Candidates</span>
          </div>
        </div>

        {/* Job 3 */}
        <div className="group cursor-pointer">
          <div className="flex justify-between items-start mb-2">
            <h4 className="text-sm font-bold text-slate-900 dark:text-slate-800 group-hover:text-primary transition-colors">Customer Success Lead</h4>
            <span className="text-[10px] font-bold text-slate-400">1w ago</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex -space-x-2">
              <img className="w-6 h-6 rounded-full border-2 border-white object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAXx9oUfqejPV0rTHnxVpqqoJo9Q5UGcR26-MugrafI8nk584AVAoZlkgI5DI4yoOBM2bN3Yw9p0WahqgIrQ9_yh1RuhbLtiGn1AuUVRZCPfCcKzR7jv-H2wfPGBhUy9emphCplY9lwAc-5X7iXq4ZzM8TV05BQWbi70DC6xgtP_pqOBdCUP2w_yWjLD2uf0AEFDJq-0L-hEhyYfpP8OWkDBwGdX42YCLv7fYKjDVPLTrf1n7G_qO_rhQ1qtyoQvVF96-ENNEJmVM8" alt="candidate" />
              <div className="w-6 h-6 rounded-full border-2 border-white bg-slate-100 dark:bg-slate-200 flex items-center justify-center text-[8px] font-bold text-slate-600">+41</div>
            </div>
            <span className="text-[10px] font-bold text-slate-600 bg-slate-100 dark:bg-slate-200 px-2 py-1 rounded">56 Candidates</span>
          </div>
        </div>
      </div>
      
      <button className="w-full mt-8 py-3 border-2 border-dashed border-slate-200 dark:border-slate-300 text-slate-500 rounded-xl text-xs font-bold hover:border-primary hover:text-primary transition-all flex items-center justify-center gap-2">
        <span className="material-symbols-outlined text-sm">add_circle</span>
        Post New Job
      </button>
    </DashboardCard>
  );
};
