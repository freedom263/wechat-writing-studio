import React, { useState, useEffect } from 'react';
import { Template, PromptConfig } from '../types';
import { getPrompts, updatePrompt } from '../api/client';
import { X, Sparkles, Save, Check, Shield } from 'lucide-react';

interface PromptModalProps {
  template: Template | null;
  onClose: () => void;
}

export const PromptModal: React.FC<PromptModalProps> = ({ template, onClose }) => {
  const [prompts, setPrompts] = useState<PromptConfig[]>([]);
  const [activeType, setActiveType] = useState<'outline' | 'article'>('outline');
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Form states
  const [systemPrompt, setSystemPrompt] = useState('');
  const [userPromptTemplate, setUserPromptTemplate] = useState('');
  const [temperature, setTemperature] = useState(0.7);
  const [appendDisclaimer, setAppendDisclaimer] = useState(false);
  const [disclaimerText, setDisclaimerText] = useState('');

  useEffect(() => {
    if (template) {
      loadPrompts();
    }
  }, [template]);

  const loadPrompts = async () => {
    if (!template) return;
    setIsLoading(true);
    try {
      const data = await getPrompts(template.id);
      setPrompts(data);
      applyPromptToForm(data, activeType);
    } catch (e: any) {
      alert(`加载提示词资产失败: ${e.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const applyPromptToForm = (list: PromptConfig[], type: 'outline' | 'article') => {
    const target = list.find((p) => p.prompt_type === type);
    if (target) {
      setSystemPrompt(target.system_prompt);
      setUserPromptTemplate(target.user_prompt_template);
      setTemperature(target.temperature);
      setAppendDisclaimer(target.append_disclaimer);
      setDisclaimerText(target.disclaimer_text || '');
    }
  };

  const handleTabChange = (type: 'outline' | 'article') => {
    setActiveType(type);
    applyPromptToForm(prompts, type);
  };

  const handleSave = async () => {
    const current = prompts.find((p) => p.prompt_type === activeType);
    if (!current) return;
    setIsSaving(true);
    setSaveSuccess(false);
    try {
      await updatePrompt(current.id, {
        system_prompt: systemPrompt,
        user_prompt_template: userPromptTemplate,
        temperature,
        append_disclaimer: appendDisclaimer,
        disclaimer_text: disclaimerText
      });
      setSaveSuccess(true);
      await loadPrompts();
      setTimeout(() => setSaveSuccess(false), 2500);
    } catch (e: any) {
      alert(`保存更新失败: ${e.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  if (!template) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 text-sm">
                提示词资产控制台 · {template.name}
              </h3>
              <p className="text-[11px] text-slate-500">
                按模板独立版本化配置，热更新无需重启服务
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200 flex items-center justify-center transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Tab switch: Outline vs Article */}
        <div className="px-6 pt-3 border-b border-slate-100 flex space-x-4">
          <button
            type="button"
            onClick={() => handleTabChange('outline')}
            className={`pb-2.5 text-xs font-bold transition-all border-b-2 ${
              activeType === 'outline'
                ? 'border-blue-600 text-blue-700'
                : 'border-transparent text-slate-500 hover:text-slate-900'
            }`}
          >
            ① 大纲生成提示词 (Outline Prompt)
          </button>
          <button
            type="button"
            onClick={() => handleTabChange('article')}
            className={`pb-2.5 text-xs font-bold transition-all border-b-2 ${
              activeType === 'article'
                ? 'border-blue-600 text-blue-700'
                : 'border-transparent text-slate-500 hover:text-slate-900'
            }`}
          >
            ② 全文正文生成提示词 (Article Prompt)
          </button>
        </div>

        {/* Body Form */}
        <div className="p-6 overflow-y-auto space-y-4 flex-1">
          {/* System Prompt */}
          <div>
            <label className="block text-xs font-bold text-slate-800 mb-1">
              System Prompt（专家人设定位与写作铁律）
            </label>
            <textarea
              rows={3}
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              className="w-full text-xs p-3 rounded-lg border border-slate-200 bg-slate-50 font-mono text-slate-800 focus:bg-white focus:ring-1 focus:ring-blue-500 focus:outline-none"
            />
          </div>

          {/* User Prompt Template with slot badges */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-xs font-bold text-slate-800">
                User Prompt 插槽模板
              </label>
              <span className="text-[10px] text-slate-400">
                支持插槽：{'{topic}'}, {'{word_count}'}, {'{tone}'}, {'{target_reader}'}, {'{outline}'}
              </span>
            </div>
            <textarea
              rows={5}
              value={userPromptTemplate}
              onChange={(e) => setUserPromptTemplate(e.target.value)}
              className="w-full text-xs p-3 rounded-lg border border-slate-200 bg-slate-50 font-mono text-slate-800 focus:bg-white focus:ring-1 focus:ring-blue-500 focus:outline-none"
            />
          </div>

          {/* Temperature */}
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-100 flex items-center justify-between">
            <div>
              <div className="text-xs font-bold text-slate-700">随机采样温度 (Temperature): {temperature}</div>
              <div className="text-[11px] text-slate-400">0.3 偏向收敛严谨，0.7 偏向发散创意</div>
            </div>
            <input
              type="range"
              min="0.1"
              max="1.0"
              step="0.05"
              value={temperature}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
              className="w-36 accent-blue-600"
            />
          </div>

          {/* Medical Compliance Disclaimer */}
          <div className="border border-emerald-100 bg-emerald-50/50 p-3.5 rounded-lg space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Shield className="w-4 h-4 text-emerald-600" />
                <span className="text-xs font-bold text-emerald-900">自动追加医疗健康合规免责声明</span>
              </div>
              <input
                type="checkbox"
                checked={appendDisclaimer}
                onChange={(e) => setAppendDisclaimer(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
            </div>
            {appendDisclaimer && (
              <input
                type="text"
                value={disclaimerText}
                onChange={(e) => setDisclaimerText(e.target.value)}
                placeholder="免责声明文字..."
                className="w-full text-xs bg-white border border-emerald-200 rounded px-2.5 py-1.5 text-slate-700"
              />
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-100 bg-slate-50 flex items-center justify-between">
          <span className="text-xs text-slate-500">
            {saveSuccess ? (
              <span className="text-emerald-700 font-bold flex items-center space-x-1">
                <Check className="w-4 h-4" />
                <span>提示词版本已更新并即刻生效！</span>
              </span>
            ) : (
              '修改后下一次生成将立即应用'
            )}
          </span>
          <div className="flex space-x-2">
            <button
              onClick={onClose}
              className="px-4 py-2 border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-semibold rounded-lg"
            >
              取消
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="px-5 py-2 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white text-xs font-bold rounded-lg flex items-center space-x-1.5 shadow-sm transition-colors"
            >
              <Save className="w-3.5 h-3.5 text-white" />
              <span className="text-white">{isSaving ? '正在保存...' : '保存并生效'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
