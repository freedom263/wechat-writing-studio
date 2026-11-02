import React, { useState, useEffect, useRef } from 'react';
import { marked } from 'marked';
import { Copy, Check, Save, Download, RotateCcw, ShieldCheck } from 'lucide-react';
import { saveArticle, saveArticleHistory } from '../api/client';

interface ArticleEditorProps {
  articleId: string;
  initialTitle: string;
  initialContent: string;
  isStreaming: boolean;
  authorName: string;
  onReset: () => void;
}

export const ArticleEditor: React.FC<ArticleEditorProps> = ({
  articleId,
  initialTitle,
  initialContent,
  isStreaming,
  authorName,
  onReset
}) => {
  const [title, setTitle] = useState(initialTitle);
  const [content, setContent] = useState(initialContent);
  const [copied, setCopied] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveNotice, setSaveNotice] = useState('');
  const autoSaveTimerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    setTitle(initialTitle);
  }, [initialTitle]);

  useEffect(() => {
    setContent(initialContent);
  }, [initialContent]);

  // 自动保存：内容变化后3秒触发
  useEffect(() => {
    if (!articleId || isStreaming) return;

    if (autoSaveTimerRef.current) {
      clearTimeout(autoSaveTimerRef.current);
    }

    autoSaveTimerRef.current = setTimeout(async () => {
      try {
        await saveArticleHistory({
          article_id: articleId,
          title,
          content,
          change_type: 'auto_save'
        });
      } catch (e) {
        console.error('自动保存历史失败:', e);
      }
    }, 3000);

    return () => {
      if (autoSaveTimerRef.current) {
        clearTimeout(autoSaveTimerRef.current);
      }
    };
  }, [title, content, articleId, isStreaming]);

  const wordCount = content.replace(/\s+/g, '').length;

  // 微信公众号富文本复制（格式完全内联，直接 Ctrl+V 到微信后台）
  const handleCopyWechatHtml = async () => {
    const rawHtml = marked.parse(content) as string;

    // 微信公众号排版样式优化
    const wechatFormattedHtml = `
      <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 16px; line-height: 1.85; color: #333333; letter-spacing: 0.5px; padding: 20px;">
        <h1 style="font-size: 22px; font-weight: bold; color: #1a1a1a; margin: 0 0 24px 0; line-height: 1.4;">${title}</h1>
        <div style="font-size: 16px; line-height: 1.85; color: #333333;">
          ${rawHtml
            .replace(/<h2>/g, '<h2 style="font-size: 20px; font-weight: bold; color: #1a1a1a; margin: 32px 0 16px 0; padding-bottom: 8px; border-bottom: 2px solid #e5e7eb;">')
            .replace(/<h3>/g, '<h3 style="font-size: 18px; font-weight: bold; color: #1a1a1a; margin: 28px 0 14px 0;">')
            .replace(/<p>/g, '<p style="margin: 16px 0; text-align: justify; text-indent: 2em;">')
            .replace(/<ul>/g, '<ul style="margin: 16px 0; padding-left: 24px;">')
            .replace(/<ol>/g, '<ol style="margin: 16px 0; padding-left: 24px;">')
            .replace(/<li>/g, '<li style="margin: 8px 0; line-height: 1.85;">')
            .replace(/<blockquote>/g, '<blockquote style="margin: 20px 0; padding: 16px 20px; background: #f9fafb; border-left: 4px solid #3b82f6; color: #64748b; font-style: italic;">')
            .replace(/<code>/g, '<code style="background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-family: Consolas, Monaco, monospace; font-size: 14px; color: #e11d48;">')
            .replace(/<pre><code/g, '<pre style="background: #1e293b; padding: 16px; border-radius: 8px; overflow-x: auto; margin: 20px 0;"><code style="color: #e2e8f0; font-family: Consolas, Monaco, monospace; font-size: 14px; background: transparent; padding: 0;"')
            .replace(/<strong>/g, '<strong style="font-weight: bold; color: #1a1a1a;">')
            .replace(/<em>/g, '<em style="font-style: italic; color: #64748b;">')
            .replace(/<a /g, '<a style="color: #3b82f6; text-decoration: none; border-bottom: 1px solid #3b82f6;" ')
          }
        </div>
      </div>
    `;

    try {
      const blobHtml = new Blob([wechatFormattedHtml], { type: 'text/html' });
      const blobText = new Blob([`${title}\n\n${content}`], { type: 'text/plain' });
      const item = new ClipboardItem({
        'text/html': blobHtml,
        'text/plain': blobText
      });
      await navigator.clipboard.write([item]);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch (e) {
      // 降级方案：纯文本复制
      await navigator.clipboard.writeText(`${title}\n\n${content}`);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  const handleSave = async () => {
    if (!articleId) return;
    setIsSaving(true);
    try {
      // 保存文章内容
      await saveArticle(articleId, {
        selected_title: title,
        final_content: content
      });
      // 保存编辑历史
      await saveArticleHistory({
        article_id: articleId,
        title,
        content,
        change_type: 'manual'
      });
      setSaveNotice('已存入草稿箱');
      setTimeout(() => setSaveNotice(''), 3000);
    } catch (e: any) {
      alert(`保存失败: ${e.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDownloadMarkdown = () => {
    const blob = new Blob([`# ${title}\n\n${content}`], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title.slice(0, 30)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const renderedPreviewHtml = marked.parse(content || '') as string;
  const hasMedicalDisclaimer = content.includes('【健康提示】') || content.includes('免责');

  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
      {/* Top Action Bar */}
      <div className="px-5 py-2.5 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <button
            onClick={onReset}
            className="text-xs text-slate-500 hover:text-slate-900 flex items-center space-x-1"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>重新创作</span>
          </button>
          <span className="text-slate-300">|</span>
          <span className="text-xs text-slate-600 font-medium">
            全文字数：<strong className="text-slate-900 font-bold">{wordCount}</strong> 字
          </span>
          {saveNotice && (
            <span className="text-xs text-emerald-600 font-medium flex items-center space-x-1">
              <Check className="w-3.5 h-3.5" />
              <span>{saveNotice}</span>
            </span>
          )}
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleSave}
            disabled={isSaving || isStreaming}
            className="px-3 py-1.5 bg-white border border-slate-300 hover:bg-slate-100 text-slate-700 rounded-lg text-xs font-semibold flex items-center space-x-1 transition-colors"
          >
            <Save className="w-3.5 h-3.5" />
            <span>保存草稿</span>
          </button>

          <button
            onClick={handleDownloadMarkdown}
            className="px-3 py-1.5 bg-white border border-slate-300 hover:bg-slate-100 text-slate-700 rounded-lg text-xs font-semibold flex items-center space-x-1 transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>导出 .md</span>
          </button>

          <button
            onClick={handleCopyWechatHtml}
            className={`px-4 py-1.5 rounded-lg text-xs font-bold flex items-center space-x-1.5 transition-colors shadow-xs ${
              copied
                ? 'bg-emerald-600 text-white'
                : 'bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white'
            }`}
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-white" />
                <span className="text-white">已复制（直接粘贴微信后台）</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5 text-white" />
                <span className="text-white">一键复制到微信公众号</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Title Input */}
      <div className="p-4 border-b border-slate-100">
        <label className="block text-[10px] font-bold text-slate-400 mb-1 uppercase tracking-wider">
          文章标题（可直接点击修改）
        </label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full text-base font-bold text-slate-900 border-none focus:outline-none focus:ring-0 p-0 placeholder-slate-300"
          placeholder="请输入或微调文章标题..."
        />
      </div>

      {/* Dual Panes */}
      <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-slate-200 min-h-[580px]">
        {/* Left: Markdown Source Editor */}
        <div className="flex flex-col bg-slate-50/40">
          <div className="px-4 py-2 bg-slate-100 border-b border-slate-200 text-xs text-slate-600 font-semibold flex items-center justify-between">
            <span>Markdown 正文编辑</span>
            {isStreaming && (
              <span className="text-[11px] text-blue-600 flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full bg-blue-600 animate-ping"></span>
                <span>正在流式撰写中...</span>
              </span>
            )}
          </div>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="flex-1 p-4 text-xs text-slate-800 font-mono bg-transparent border-none focus:outline-none resize-none leading-relaxed"
            placeholder="正文内容..."
          />
        </div>

        {/* Right: WeChat Preview */}
        <div className="flex flex-col bg-white">
          <div className="px-4 py-2 bg-slate-100 border-b border-slate-200 text-xs text-slate-600 font-semibold flex items-center justify-between">
            <span>微信文章排版效果预览</span>
            {hasMedicalDisclaimer && (
              <span className="text-[10px] text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 flex items-center space-x-1">
                <ShieldCheck className="w-3 h-3 text-emerald-600" />
                <span>医疗健康合规免责护栏已生效</span>
              </span>
            )}
          </div>

          <div className="flex-1 p-6 overflow-y-auto max-h-[620px]">
            {/* WeChat Header Article Meta */}
            <div className="mb-6 pb-4 border-b border-slate-100">
              <h2 className="text-xl font-bold text-slate-900 leading-snug mb-3">
                {title || '暂无标题'}
              </h2>
              <div className="flex items-center space-x-3 text-xs text-slate-400">
                <span className="text-blue-700 font-semibold">{authorName}</span>
                <span>今日</span>
                <span>原创</span>
              </div>
            </div>

            {/* Rendered HTML */}
            <div
              className="wechat-preview text-sm leading-relaxed"
              dangerouslySetInnerHTML={{ __html: renderedPreviewHtml }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
