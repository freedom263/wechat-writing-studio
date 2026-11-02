import React, { useState, useEffect } from 'react';
import { Key, Check, X, ShieldAlert, Sparkles, ExternalLink } from 'lucide-react';

interface ApiKeyModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const ApiKeyModal: React.FC<ApiKeyModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [apiKey, setApiKey] = useState('');
  const [currentMaskedKey, setCurrentMaskedKey] = useState('');
  const [hasKey, setHasKey] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [notice, setNotice] = useState('');

  useEffect(() => {
    if (isOpen) {
      fetch('/api/v1/settings/status')
        .then((r) => r.json())
        .then((data) => {
          setHasKey(data.has_key);
          setCurrentMaskedKey(data.masked_key);
        })
        .catch(console.error);
    }
  }, [isOpen]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!apiKey.trim()) return;
    setIsSaving(true);
    try {
      const res = await fetch('/api/v1/settings/api-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey.trim() })
      });
      if (!res.ok) throw new Error('保存失败');
      setNotice('DeepSeek API Key 设置成功，已即刻激活真实大模型！');
      setApiKey('');
      setTimeout(() => {
        onSuccess();
        onClose();
        setNotice('');
      }, 1500);
    } catch (err: any) {
      alert(`设置失败: ${err.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-md w-full shadow-2xl border border-slate-200 overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center">
              <Key className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 text-sm">DeepSeek 模型 API 配置</h3>
              <p className="text-[11px] text-slate-500">直连官方接口，解锁万亿级深度大模型思考</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSave} className="p-5 space-y-4">
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-slate-500">当前连接状态：</span>
              <span className={`font-bold ${hasKey ? 'text-emerald-700' : 'text-amber-700'}`}>
                {hasKey ? `已连接 (${currentMaskedKey})` : '未配置（运行本地深度推理引擎）'}
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              未填 Key 时，系统会自动调用本地深度文学与专业知识推理引擎。
            </p>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              DeepSeek API Key (sk-...)
            </label>
            <input
              type="password"
              placeholder="请输入你在 platform.deepseek.com 申请的 API Key"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:bg-white focus:ring-1 focus:ring-blue-500 focus:outline-none font-mono"
            />
          </div>

          <div className="text-[11px] text-slate-500 flex items-center justify-between">
            <span>还没有 API Key？</span>
            <a
              href="https://platform.deepseek.com/"
              target="_blank"
              rel="noreferrer"
              className="text-blue-600 hover:underline flex items-center space-x-0.5 font-semibold"
            >
              <span>前往 DeepSeek 官方申请</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>

          {notice && (
            <div className="p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 font-semibold flex items-center space-x-1.5">
              <Check className="w-4 h-4 text-emerald-600" />
              <span>{notice}</span>
            </div>
          )}

          <div className="pt-2 flex space-x-2 justify-end">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-semibold rounded-lg"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={isSaving || !apiKey.trim()}
              className="px-5 py-2 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white text-xs font-bold rounded-lg shadow-sm disabled:opacity-50 transition-colors"
            >
              {isSaving ? '正在验证保存...' : '保存并激活'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
