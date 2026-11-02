import React, { useState, useEffect } from 'react';
import { Article } from '../types';
import { getArticles } from '../api/client';
import { FileText, ArrowRight, Loader2 } from 'lucide-react';

interface DraftsViewProps {
  onSelectArticle: (art: Article) => void;
}

export const DraftsView: React.FC<DraftsViewProps> = ({ onSelectArticle }) => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDrafts();
  }, []);

  const loadDrafts = async () => {
    setIsLoading(true);
    try {
      const data = await getArticles();
      setArticles(data);
    } catch (e: any) {
      alert(`获取文章列表失败: ${e.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900">草稿与历史文章库</h2>
          <p className="text-xs text-slate-500 mt-1">本地数据库自动实时持久化保存的所有创作成果</p>
        </div>
        <button
          onClick={loadDrafts}
          className="text-xs text-blue-700 hover:text-blue-900 hover:underline font-semibold"
        >
          刷新列表
        </button>
      </div>

      {isLoading ? (
        <div className="py-20 flex flex-col items-center justify-center text-slate-400 space-y-2">
          <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
          <span className="text-xs">加载文章库...</span>
        </div>
      ) : articles.length === 0 ? (
        <div className="py-20 text-center bg-white rounded-2xl border border-dashed border-slate-300 p-8">
          <FileText className="w-10 h-10 text-slate-300 mx-auto mb-2" />
          <p className="text-sm font-medium text-slate-600">暂无草稿或历史生成文章</p>
          <p className="text-xs text-slate-400 mt-1">点击左侧“开始创作”，体验从灵感到成稿的极速生成</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {articles.map((art) => (
            <div
              key={art.id}
              onClick={() => onSelectArticle(art)}
              className="bg-white p-5 rounded-xl border border-slate-200 hover:border-blue-400 hover:shadow-md transition-all cursor-pointer flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                    art.status === 'completed'
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      : 'bg-amber-50 text-amber-800 border border-amber-200'
                  }`}>
                    {art.status === 'completed' ? '已生成正文' : '大纲草稿'}
                  </span>
                  <span className="text-[11px] text-slate-400">
                    {art.word_count || 0} 字
                  </span>
                </div>

                <h3 className="font-bold text-slate-900 text-sm mb-2 line-clamp-1">
                  {art.selected_title || art.raw_input || '未命名文章'}
                </h3>

                <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed mb-4">
                  {art.final_content?.slice(0, 100) || art.outline_content?.slice(0, 100) || '暂无正文预览'}
                </p>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
                <span>{art.created_at ? new Date(art.created_at).toLocaleString() : '刚刚'}</span>
                <span className="text-blue-700 font-semibold flex items-center space-x-1 group-hover:translate-x-1 transition-transform">
                  <span>进入排版</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
