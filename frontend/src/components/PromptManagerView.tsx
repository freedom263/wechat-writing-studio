import React, { useState, useEffect } from 'react';
import { Category, Template } from '../types';
import { getCategories } from '../api/client';
import { Sparkles, Edit3, Shield } from 'lucide-react';
import { PromptModal } from './PromptModal';

export const PromptManagerView: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);

  useEffect(() => {
    getCategories().then(setCategories).catch(console.error);
  }, []);

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900 flex items-center space-x-2">
          <Sparkles className="w-5 h-5 text-blue-600" />
          <span>提示词资产与版本管理中台</span>
        </h2>
        <p className="text-xs text-slate-500 mt-1">
          提示词已解耦为独立资产库。支持对 11 大赛道中各模板的大纲与正文提示词进行在线热调优，即改即生效。
        </p>
      </div>

      <div className="space-y-5">
        {categories.map((cat) => (
          <div key={cat.id} className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
            <div className="flex items-center space-x-2 pb-3 mb-3 border-b border-slate-100">
              <span className="w-2.5 h-2.5 rounded-full bg-blue-600"></span>
              <h3 className="font-bold text-sm text-slate-900">{cat.name}</h3>
              <span className="text-xs text-slate-400">（{cat.templates.length} 款模板）</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
              {cat.templates.map((tpl) => (
                <div
                  key={tpl.id}
                  className="p-3.5 rounded-lg border border-slate-200 bg-slate-50/50 hover:bg-white hover:border-blue-300 hover:shadow-xs transition-all flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="font-bold text-xs text-slate-900">{tpl.name}</span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-white text-slate-600 border border-slate-200">
                        {tpl.tag}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500 line-clamp-2 leading-relaxed">
                      {tpl.description}
                    </p>
                  </div>

                  <div className="mt-3 pt-2 border-t border-slate-200 flex items-center justify-between">
                    <span className="text-[10px] text-emerald-700 flex items-center space-x-1 font-medium">
                      <Shield className="w-3 h-3 text-emerald-600" />
                      <span>{cat.id === 'tcm_health' ? '医疗合规' : '通用合规'}</span>
                    </span>
                    <button
                      onClick={() => setSelectedTemplate(tpl)}
                      className="px-2.5 py-1 bg-white hover:bg-blue-50 text-blue-700 border border-blue-200 rounded text-xs font-semibold flex items-center space-x-1 shadow-2xs transition-colors"
                    >
                      <Edit3 className="w-3 h-3" />
                      <span>编辑Prompt</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {selectedTemplate && (
        <PromptModal
          template={selectedTemplate}
          onClose={() => setSelectedTemplate(null)}
        />
      )}
    </div>
  );
};
