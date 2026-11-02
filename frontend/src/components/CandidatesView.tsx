import React, { useState } from 'react';
import { OutlineCandidate } from '../types';
import { CheckCircle, ArrowRight, Sparkles, Layers, ChevronDown, ChevronUp, Eye } from 'lucide-react';

interface CandidatesViewProps {
  candidates: OutlineCandidate[];
  onConfirmGenerateArticle: (candidate: OutlineCandidate) => void;
  isGeneratingArticle: boolean;
}

export const CandidatesView: React.FC<CandidatesViewProps> = ({
  candidates,
  onConfirmGenerateArticle,
  isGeneratingArticle
}) => {
  const [selectedIndex, setSelectedIndex] = useState<number>(1);
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  const [previewMode, setPreviewMode] = useState(false);

  const selectedCandidate = candidates.find((c) => c.index === selectedIndex) || candidates[0];

  const toggleExpand = (index: number) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-4 shadow-xs">
      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
        <div>
          <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-blue-600" />
            <span>AI 为你构思的 3 组差异化方案</span>
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            点击卡片选择方案，点击"查看完整大纲"展开详情对比
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setPreviewMode(!previewMode)}
            className={`text-xs px-3 py-1.5 rounded-md font-medium border transition-colors flex items-center space-x-1 ${
              previewMode
                ? 'bg-blue-50 text-blue-700 border-blue-200'
                : 'bg-slate-100 text-slate-700 border-slate-200 hover:bg-slate-200'
            }`}
          >
            <Eye className="w-3.5 h-3.5" />
            <span>{previewMode ? '预览模式' : '卡片模式'}</span>
          </button>
          <div className="text-xs bg-slate-100 text-slate-700 px-2.5 py-1 rounded-md font-medium border border-slate-200">
            已就绪 3 组方案
          </div>
        </div>
      </div>

      {/* Candidate Cards Grid */}
      <div className={`grid gap-3 ${previewMode ? 'grid-cols-1' : 'grid-cols-1 md:grid-cols-3'}`}>
        {candidates.map((cand) => {
          const isSelected = cand.index === selectedIndex;
          const isExpanded = expandedIndex === cand.index;

          return (
            <div
              key={cand.index}
              className={`rounded-xl border transition-all ${
                isSelected
                  ? 'border-blue-600 bg-blue-50/20 ring-2 ring-blue-600 shadow-xs'
                  : 'border-slate-200 bg-slate-50/40 hover:border-slate-300'
              }`}
            >
              <div
                onClick={() => setSelectedIndex(cand.index)}
                className="p-4 cursor-pointer"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className={`text-[11px] font-bold px-2 py-0.5 rounded ${
                    isSelected ? 'bg-blue-600 text-white' : 'bg-slate-200 text-slate-700'
                  }`}>
                    方案 {cand.index}
                  </span>
                  {isSelected && <CheckCircle className="w-4 h-4 text-blue-600" />}
                </div>

                <h4 className="text-xs font-bold text-slate-900 mb-2 leading-snug line-clamp-2">
                  {cand.title}
                </h4>

                <p className="text-[11px] text-slate-500 leading-relaxed mb-3 line-clamp-2">
                  {cand.summary}
                </p>

                {/* Tags */}
                <div className="flex flex-wrap gap-1 mb-3">
                  {cand.tags?.map((t, idx) => (
                    <span
                      key={idx}
                      className="text-[10px] px-1.5 py-0.5 rounded bg-white border border-slate-200 text-slate-600"
                    >
                      {t}
                    </span>
                  ))}
                </div>

                {/* Outline snippet preview */}
                {!isExpanded && (
                  <div className="bg-white p-2.5 rounded-lg border border-slate-200 text-[11px] text-slate-600 space-y-1">
                    <div className="font-semibold text-slate-700 text-[10px] flex items-center space-x-1 mb-1">
                      <Layers className="w-3 h-3 text-blue-600" />
                      <span>大纲结构速览：</span>
                    </div>
                    {cand.outline_sections?.slice(0, 3).map((sec, sIdx) => (
                      <div key={sIdx} className="truncate text-slate-500">
                        • {sec}
                      </div>
                    ))}
                    {cand.outline_sections && cand.outline_sections.length > 3 && (
                      <div className="text-[10px] text-slate-400">...共 {cand.outline_sections.length} 个小节</div>
                    )}
                  </div>
                )}
              </div>

              {/* Expandable Full Outline */}
              {cand.outline_sections && cand.outline_sections.length > 0 && (
                <div className="border-t border-slate-200">
                  <button
                    onClick={() => toggleExpand(cand.index)}
                    className="w-full px-4 py-2 text-[11px] font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-50 flex items-center justify-between transition-colors"
                  >
                    <span>{isExpanded ? '收起完整大纲' : '查看完整大纲'}</span>
                    {isExpanded ? (
                      <ChevronUp className="w-3.5 h-3.5" />
                    ) : (
                      <ChevronDown className="w-3.5 h-3.5" />
                    )}
                  </button>

                  {isExpanded && (
                    <div className="px-4 pb-4 space-y-2 animate-fade-in">
                      <div className="bg-gradient-to-br from-slate-50 to-white p-3 rounded-lg border border-slate-200">
                        <div className="text-[10px] font-bold text-slate-700 mb-2 flex items-center space-x-1">
                          <Layers className="w-3 h-3 text-blue-600" />
                          <span>完整大纲结构（共 {cand.outline_sections.length} 个小节）</span>
                        </div>
                        <div className="space-y-1.5">
                          {cand.outline_sections.map((sec, sIdx) => (
                            <div
                              key={sIdx}
                              className="text-[11px] text-slate-700 leading-relaxed pl-2 border-l-2 border-blue-200 py-0.5"
                            >
                              <span className="font-semibold text-blue-700 mr-1">{sIdx + 1}.</span>
                              {sec}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Action bar */}
      <div className="pt-2 flex items-center justify-between">
        <div className="text-xs text-slate-500">
          当前选中：<strong className="text-slate-800">方案 {selectedIndex}</strong> · 《{selectedCandidate.title}》
        </div>
        <button
          onClick={() => onConfirmGenerateArticle(selectedCandidate)}
          disabled={isGeneratingArticle}
          className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-bold rounded-lg text-xs flex items-center space-x-2 shadow-sm transition-colors disabled:opacity-50 cursor-pointer"
        >
          <span>以此大纲进入全文写作与排版</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
