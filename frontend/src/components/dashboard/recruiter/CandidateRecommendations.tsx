import React from 'react';
import { DashboardCard } from '../shared/DashboardCard';

export const CandidateRecommendations: React.FC = () => {
  return (
    <div className="space-y-6 mb-8">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-bold font-headline text-slate-900 dark:text-slate-800">Top Recommended Candidates</h3>
        <div className="flex gap-2">
          <span className="px-3 py-1 bg-primary-fixed text-on-primary-fixed-variant text-[10px] font-bold rounded-full uppercase">AI-Ranked</span>
          <span className="px-3 py-1 bg-slate-100 text-slate-600 text-[10px] font-bold rounded-full uppercase">High Potential</span>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Candidate 1 */}
        <DashboardCard className="!p-6 border-l-4 border-l-primary-container relative overflow-hidden group hover:shadow-xl hover:shadow-slate-200/50 transition-all">
          <div className="flex justify-between items-start mb-4">
            <div className="flex items-center gap-3">
              <img className="w-12 h-12 rounded-xl object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuB3qrIwZBwDmUp-gLp5hRADIDSTr95VjqcpDnH35jwSTLV2GtYlpHnPJaGFudaiXu7XkfmTnVKPbmhyaW91cX2PHZsFW6ATvgzn5rX_3qk4Vd9f3eS9HbeQJafZVrDx5MQWEgaQPz3iSOPlM5Z3JIwdkuOifZckn7cuMI9MO_k036WoKtbDP__wqPIeVG1nJGok7-8IKZfzi0vcbr8YtgrsGOiZEm5Og6LNR_zgMdXDR5qfMgZZgk7nLtBbJGLzmN-jSrUjnobPCBI" alt="Leo Volkov" />
              <div>
                <p className="text-sm font-bold text-slate-900 dark:text-slate-800">Leo Volkov</p>
                <p className="text-[10px] text-slate-500">Staff Frontend Engineer</p>
              </div>
            </div>
            <div className="bg-primary/5 px-2 py-1 rounded text-primary font-bold text-sm">9.4</div>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center text-[10px]">
              <span className="text-slate-500">Technical Depth</span>
              <div className="w-24 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                <div className="w-[95%] h-full bg-primary-container"></div>
              </div>
            </div>
            <div className="flex justify-between items-center text-[10px]">
              <span className="text-slate-500">Communication</span>
              <div className="w-24 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                <div className="w-[88%] h-full bg-primary-container"></div>
              </div>
            </div>
            <div className="flex justify-between items-center text-[10px]">
              <span className="text-slate-500">Culture Fit</span>
              <div className="w-24 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                <div className="w-[92%] h-full bg-primary-container"></div>
              </div>
            </div>
          </div>
          <div className="mt-6 flex gap-2">
            <button className="flex-1 py-2 bg-primary text-white text-[10px] font-bold rounded-lg hover:bg-blue-700">Review Profile</button>
            <button className="p-2 bg-slate-50 dark:bg-slate-200 text-slate-400 rounded-lg hover:text-primary transition-colors">
              <span className="material-symbols-outlined text-sm">bookmark</span>
            </button>
          </div>
        </DashboardCard>

        {/* Candidate 2 */}
        <DashboardCard className="!p-6 border-l-4 border-l-primary-container relative overflow-hidden group hover:shadow-xl hover:shadow-slate-200/50 transition-all">
          <div className="flex justify-between items-start mb-4">
            <div className="flex items-center gap-3">
              <img className="w-12 h-12 rounded-xl object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCcJXficxnO1ageRSpQr-QznmHPlE73kdXnAjye47FbD5BGn6b7GizHbchv1PoXlKYIHG9giFuzMIm1GedQMibJWx2ksHdm1xcIiSmUa30rhHTlTqDM3qiDQeF1G2-rhJE7Kbt--ykrpe-Cvre35mrjfVqr6YtV_lkuDWj9NUeYI_hxnNySBcm34DYveVZheuzOPXTFHgEJm1VPcwT7X7v32QyREdhej1POfr2JbpcgT8WuvPyRkmcBj7QdTaNyBfNjpTOGJsUEo6U" alt="Elena Rodri" />
              <div>
                <p className="text-sm font-bold text-slate-900 dark:text-slate-800">Elena Rodri</p>
                <p className="text-[10px] text-slate-500">Product Lead</p>
              </div>
            </div>
            <div className="bg-primary/5 px-2 py-1 rounded text-primary font-bold text-sm">9.1</div>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center text-[10px]">
              <span className="text-slate-500">Technical Depth</span>
              <div className="w-24 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                <div className="w-[82%] h-full bg-primary-container"></div>
              </div>
            </div>
            <div className="flex justify-between items-center text-[10px]">
              <span className="text-slate-500">Communication</span>
              <div className="w-24 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                <div className="w-[96%] h-full bg-primary-container"></div>
              </div>
            </div>
            <div className="flex justify-between items-center text-[10px]">
              <span className="text-slate-500">Culture Fit</span>
              <div className="w-24 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                <div className="w-[94%] h-full bg-primary-container"></div>
              </div>
            </div>
          </div>
          <div className="mt-6 flex gap-2">
            <button className="flex-1 py-2 bg-primary text-white text-[10px] font-bold rounded-lg hover:bg-blue-700">Review Profile</button>
            <button className="p-2 bg-slate-50 dark:bg-slate-200 text-slate-400 rounded-lg hover:text-primary transition-colors">
              <span className="material-symbols-outlined text-sm">bookmark</span>
            </button>
          </div>
        </DashboardCard>

        {/* Candidate 3 */}
        <DashboardCard className="!p-6 border-l-4 border-l-primary-container relative overflow-hidden group hover:shadow-xl hover:shadow-slate-200/50 transition-all">
          <div className="flex justify-between items-start mb-4">
            <div className="flex items-center gap-3">
              <img className="w-12 h-12 rounded-xl object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDRFKc1xiSLTZtk0MuJnKBLFKIinTR4EsgnQMESn3MnynkxxqLS-coz0LxihUU03JkeNU0gjUCBgJGVK0DqKelzK3wzk74BzoPZ-8xe4RwqWW1ZS3uQt9JTz0x7MFe37GwybsRLpQKwuJb___SWQAljZmPvG9DO5LyCHjgRSm89NePpAkyAhVrdG8CL84Tzm14mBCiAwSCI3Va7SXJWLvYmWhV7yax6tkJaQtTIR6eRuo8SWu6Cx_4Af5Oyk_iBjC3026ji6lRmjQ0" alt="Yuki Sato" />
              <div>
                <p className="text-sm font-bold text-slate-900 dark:text-slate-800">Yuki Sato</p>
                <p className="text-[10px] text-slate-500">Fullstack Engineer</p>
              </div>
            </div>
            <div className="bg-primary/5 px-2 py-1 rounded text-primary font-bold text-sm">8.9</div>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center text-[10px]">
              <span className="text-slate-500">Technical Depth</span>
              <div className="w-24 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                <div className="w-[90%] h-full bg-primary-container"></div>
              </div>
            </div>
            <div className="flex justify-between items-center text-[10px]">
              <span className="text-slate-500">Communication</span>
              <div className="w-24 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                <div className="w-[84%] h-full bg-primary-container"></div>
              </div>
            </div>
            <div className="flex justify-between items-center text-[10px]">
              <span className="text-slate-500">Culture Fit</span>
              <div className="w-24 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                <div className="w-[80%] h-full bg-primary-container"></div>
              </div>
            </div>
          </div>
          <div className="mt-6 flex gap-2">
            <button className="flex-1 py-2 bg-primary text-white text-[10px] font-bold rounded-lg hover:bg-blue-700">Review Profile</button>
            <button className="p-2 bg-slate-50 dark:bg-slate-200 text-slate-400 rounded-lg hover:text-primary transition-colors">
              <span className="material-symbols-outlined text-sm">bookmark</span>
            </button>
          </div>
        </DashboardCard>
      </div>
    </div>
  );
};
