import React from 'react';
import { DashboardCard } from '../shared/DashboardCard';

export const ScheduleWidget: React.FC = () => {
  return (
    <DashboardCard>
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-bold font-headline text-slate-900 dark:text-slate-800">Today's Schedule</h3>
        <span className="text-[10px] font-bold px-2 py-1 bg-slate-100 text-slate-500 uppercase rounded-full">Aug 24</span>
      </div>
      <div className="space-y-4">
        {/* Event 1 */}
        <div className="flex items-center gap-4 p-3 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-100 transition-all border border-transparent hover:border-slate-100">
          <div className="w-10 h-10 rounded-full bg-slate-200 overflow-hidden">
            <img className="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBzSexM6S8dg5nVFs5jyBgvORsMYLtwgpMPAb7Ld8MHLk_MzCXPJ3d4ChAXT9EU2dSkSbicaf-Z6dqBCadpRp7nRKYXZa7U2vFq0EulPR3XyG--mOlIBGLcgCUUPO_TmrcnBYVxJoib6h1xOiw01EXSUgHfiJ2NY43FYeNagkbOFe72cGsrnYt9x7G9vx_uM-uIny_VffzzPeJGaioA8WsrU3eUYs5sC19zUwkvcqpGdDGso5mhmv1L18_qpE1RoVP0cEiU6gKpEEI" alt="Marcus Chen" />
          </div>
          <div className="flex-1">
            <p className="text-xs font-bold text-slate-900 dark:text-slate-800">Marcus Chen</p>
            <p className="text-[10px] text-slate-500">Sr. Product Designer • 10:30 AM</p>
          </div>
          <button className="px-3 py-1.5 bg-primary text-white text-[10px] font-bold rounded-lg hover:bg-blue-700">Join</button>
        </div>

        {/* Event 2 */}
        <div className="flex items-center gap-4 p-3 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-100 transition-all border border-transparent hover:border-slate-100">
          <div className="w-10 h-10 rounded-full bg-slate-200 overflow-hidden">
            <img className="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDZOhne_reyFMIyhD-aDPXJz1iFh962ffc-ogsQfeJzIwGpC3do2L9X3oB8deskypa1kRSG83tsyDWTzwn8Aj5N1lOZcAvuOf5z-KzHgLeYTRO2Tnj7OGEY6ym_kesyvXi1cKazhm_AsA5QQXPPcXPQl7uFpPkbfFkT8RtBI4Y0IOLrAMuB6_DoFsFO3gtr3KkOtA-ShE2j8jFJKZkCQeWl2CZiK1IqWGF0Zgd_TPKlOe7Ai7NrS_3v7oclE9EZshDNAsgesS2p6Ds" alt="Sarah Jenkins" />
          </div>
          <div className="flex-1">
            <p className="text-xs font-bold text-slate-900 dark:text-slate-800">Sarah Jenkins</p>
            <p className="text-[10px] text-slate-500">Backend Engineer • 1:15 PM</p>
          </div>
          <button className="px-3 py-1.5 bg-surface-container text-slate-600 text-[10px] font-bold rounded-lg cursor-not-allowed">Wait</button>
        </div>

        {/* Event 3 */}
        <div className="flex items-center gap-4 p-3 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-100 transition-all border border-transparent hover:border-slate-100">
          <div className="w-10 h-10 rounded-full bg-slate-200 overflow-hidden">
            <img className="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuC7tTUJOe5wgwQHBmVXzEMLMKRvSXWVBeTWcadfLsxEs_QhUSS9WTnReHubqGQ9yzHTz0dAkkPimpG8RlBF19N16ZP6TqSftjQP2Omzv-FhPoxbbqy2p64j5v9SZ-dnmyyM97K21LhQraYez401ZKD33xB-t8rKUU9qJJg51B6dBpgLeyiiuZbPPmhUPk--uja23lXo54bLekaVVEU2vCV2QtZ9KaJIqtpt5Rl59ca2bjicWs8uSjc24Ucgs1xte0dm7H410g-pO8w" alt="Amara Okafor" />
          </div>
          <div className="flex-1">
            <p className="text-xs font-bold text-slate-900 dark:text-slate-800">Amara Okafor</p>
            <p className="text-[10px] text-slate-500">Marketing Lead • 3:45 PM</p>
          </div>
          <button className="px-3 py-1.5 bg-surface-container text-slate-600 text-[10px] font-bold rounded-lg cursor-not-allowed">Wait</button>
        </div>
      </div>
      <button className="w-full mt-6 py-2.5 text-[11px] font-bold text-slate-500 bg-slate-50 hover:bg-slate-100 rounded-xl transition-all">
        View Full Calendar
      </button>
    </DashboardCard>
  );
};
