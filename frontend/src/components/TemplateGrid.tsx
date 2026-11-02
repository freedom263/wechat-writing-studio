import React from 'react';
import { Template } from '../types';
import { Check, Settings2 } from 'lucide-react';

interface TemplateGridProps {
  templates: Template[];
  selectedTemplateId: string;
  onSelectTemplate: (tpl: Template) => void;
  onOpenPromptModal: (tpl: Template) => void;
}

export const TemplateGrid: React.FC<TemplateGridProps> = ({
  templates,
  selectedTemplateId,
  onSelectTemplate,
  onOpenPromptModal
}) => {
  return (
    <div className="space-y-2.5">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-bold text-slate-800 flex items-center space-x-2">
          <span>选择写作模板</span>
          <span className="text-xs font-normal text-slate-400">（共 {templates.length} 款）</span>
        </h3>
      </div>

      <div className="grid grid-cols-2 gap-2.5">
        {templates.map((tpl) => {
          const isSelected = tpl.id === selectedTemplateId;
          return (
            <div
              key={tpl.id}
              onClick={() => onSelectTemplate(tpl)}
              className={`relative p-3 rounded-xl border transition-smooth cursor-pointer flex flex-col justify-between hover-lift ${
                isSelected
                  ? 'border-blue-600 bg-blue-50/20 ring-1 ring-blue-600 shadow-xs'
                  : 'border-slate-200 bg-white hover:border-slate-300 hover:shadow-md'
              }`}
            >
              {/* Checkmark icon for selected */}
              {isSelected && (
                <div className="absolute top-2 right-2 w-4 h-4 rounded-full bg-blue-600 text-white flex items-center justify-center animate-fade-in">
                  <Check className="w-3 h-3 stroke-[3]" />
                </div>
              )}

              <div>
                <div className="flex items-center space-x-2 mb-1">
                  <h4 className={`text-xs font-bold ${isSelected ? 'text-blue-900' : 'text-slate-900'}`}>
                    {tpl.name}
                  </h4>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 font-medium">
                    {tpl.tag}
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 line-clamp-2 leading-relaxed">
                  {tpl.description}
                </p>
              </div>

              {/* Action bar on bottom */}
              <div className="mt-2.5 pt-2 border-t border-slate-100 flex items-center justify-between text-[11px]">
                <span className="text-slate-400 text-[10px]">内置提示词</span>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onOpenPromptModal(tpl);
                  }}
                  className="text-slate-500 hover:text-blue-600 flex items-center space-x-1 hover:underline transition-colors"
                >
                  <Settings2 className="w-3 h-3" />
                  <span>调优Prompt</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
