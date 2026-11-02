import React, { useEffect, useState } from 'react';
import { PenTool, Inbox, Sparkles, AlertCircle, CheckCircle } from 'lucide-react';
import { getModeInfo } from '../api/client';

interface SidebarProps {
  currentTab: 'create' | 'drafts' | 'prompts';
  setCurrentTab: (tab: 'create' | 'drafts' | 'prompts') => void;
  selectedAccount: string;
  setSelectedAccount: (acc: string) => void;
  onOpenApiKeyModal?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  setCurrentTab,
  selectedAccount,
  setSelectedAccount,
  onOpenApiKeyModal
}) => {
  const [modeInfo, setModeInfo] = useState<{ is_demo_mode: boolean; mode: string; description: string } | null>(null);

  useEffect(() => {
    getModeInfo()
      .then(setModeInfo)
      .catch(() => setModeInfo(null));
  }, []);

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col justify-between shrink-0 h-screen select-none sticky top-0">
      <div>
        {/* Brand / Logo */}
        <div className="p-5 border-b border-slate-100 flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-slate-900 flex items-center justify-center text-white shadow-sm">
            <PenTool className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h1 className="font-bold text-slate-900 tracking-tight text-base leading-tight">文思 · 写作台</h1>
            <p className="text-[11px] text-slate-400 font-medium">公众号智能创作工作室</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="p-3 space-y-1 mt-2">
          <button
            onClick={() => setCurrentTab('create')}
            className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-xs font-semibold transition-colors ${
              currentTab === 'create'
                ? 'bg-blue-50 text-blue-700 shadow-2xs font-bold'
                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
            }`}
          >
            <PenTool className={`w-4 h-4 ${currentTab === 'create' ? 'text-blue-600' : 'text-slate-400'}`} />
            <span>开始创作</span>
          </button>

          <button
            onClick={() => setCurrentTab('drafts')}
            className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-xs font-semibold transition-colors ${
              currentTab === 'drafts'
                ? 'bg-blue-50 text-blue-700 shadow-2xs font-bold'
                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
            }`}
          >
            <Inbox className={`w-4 h-4 ${currentTab === 'drafts' ? 'text-blue-600' : 'text-slate-400'}`} />
            <span>草稿与文章库</span>
          </button>

          <button
            onClick={() => setCurrentTab('prompts')}
            className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-xs font-semibold transition-colors ${
              currentTab === 'prompts'
                ? 'bg-blue-50 text-blue-700 shadow-2xs font-bold'
                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
            }`}
          >
            <Sparkles className={`w-4 h-4 ${currentTab === 'prompts' ? 'text-blue-600' : 'text-slate-400'}`} />
            <span>提示词资产中台</span>
          </button>
        </nav>
      </div>

      {/* Footer / Account Profile */}
      <div className="p-4 border-t border-slate-100 bg-slate-50/60">
        <div className="text-[11px] font-medium text-slate-500 mb-1.5">当前挂载公众号</div>
        <select
          value={selectedAccount}
          onChange={(e) => setSelectedAccount(e.target.value)}
          className="w-full bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-700 font-medium focus:outline-none focus:ring-1 focus:ring-blue-500 mb-3"
        >
          <option value="知行笔记">知行笔记 (个人综合号)</option>
          <option value="健康科普专栏">健康科普专栏 (医疗养生号)</option>
          <option value="产品观察笔记">产品观察笔记 (科技商业号)</option>
        </select>

        <div
          onClick={onOpenApiKeyModal}
          className="flex items-center justify-between text-[11px] text-slate-700 bg-white hover:bg-blue-50/60 px-2.5 py-1.5 rounded-md border border-slate-200 cursor-pointer transition-colors"
          title="点击配置真实 DeepSeek API Key"
        >
          <span className="flex items-center space-x-1.5 font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-600 animate-pulse"></span>
            <span>模型引擎配置</span>
          </span>
          <span className="font-semibold text-blue-700 hover:underline">API Key</span>
        </div>

        {/* Runtime Mode Indicator */}
        {modeInfo && (
          <div
            className={`mt-2 px-2.5 py-1.5 rounded-md border text-[11px] font-medium flex items-center space-x-1.5 ${
              modeInfo.is_demo_mode
                ? 'bg-amber-50 border-amber-200 text-amber-800'
                : 'bg-green-50 border-green-200 text-green-800'
            }`}
            title={modeInfo.description}
          >
            {modeInfo.is_demo_mode ? (
              <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
            ) : (
              <CheckCircle className="w-3.5 h-3.5 text-green-600" />
            )}
            <span>{modeInfo.mode}</span>
          </div>
        )}
      </div>
    </aside>
  );
};
