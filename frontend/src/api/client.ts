import { Category, PromptConfig, Article, OutlineCandidate } from '../types';

// 支持生产环境动态配置后端地址
const API_BASE = import.meta.env.VITE_API_BASE_URL
  ? `${import.meta.env.VITE_API_BASE_URL}/api/v1`
  : '/api/v1';

export async function getCategories(): Promise<Category[]> {
  const res = await fetch(`${API_BASE}/categories`);
  if (!res.ok) throw new Error('获取赛道分类失败');
  return res.json();
}

export async function getPrompts(templateId: string): Promise<PromptConfig[]> {
  const res = await fetch(`${API_BASE}/prompts/${templateId}`);
  if (!res.ok) throw new Error('获取提示词失败');
  return res.json();
}

export async function updatePrompt(promptId: string, payload: Partial<PromptConfig>): Promise<PromptConfig> {
  const res = await fetch(`${API_BASE}/prompts/${promptId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('更新提示词失败');
  return res.json();
}

export async function parseUrl(url: string): Promise<{ title: string; clean_content: string; summary: string }> {
  const res = await fetch(`${API_BASE}/creation/parse-url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: '链接提取失败' }));
    throw new Error(err.detail || '链接提取失败');
  }
  return res.json();
}

/** 零散关键词智能意图理解与主题扩写 (支持换一换) */
export async function expandTopic(params: {
  category_id: string;
  template_id: string;
  keywords: string;
  tone?: string;
  target_reader?: string;
  batch?: number;
}): Promise<{ suggestions: Array<{ topic: string; supplementary: string }> }> {
  const res = await fetch(`${API_BASE}/creation/expand-topic?batch=${params.batch || 1}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  });
  if (!res.ok) throw new Error('AI 扩写生成失败');
  return res.json();
}

export async function getArticles(): Promise<Article[]> {
  const res = await fetch(`${API_BASE}/articles`);
  if (!res.ok) throw new Error('获取草稿失败');
  return res.json();
}

export async function getArticle(articleId: string): Promise<Article> {
  const res = await fetch(`${API_BASE}/articles/${articleId}`);
  if (!res.ok) throw new Error('获取文章详情失败');
  return res.json();
}

export async function saveArticle(articleId: string, payload: { final_content?: string; selected_title?: string }) {
  const res = await fetch(`${API_BASE}/articles/${articleId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('保存草稿失败');
  return res.json();
}

export async function getModeInfo(): Promise<{ is_demo_mode: boolean; mode: string; description: string }> {
  const res = await fetch(`${API_BASE}/settings/mode`);
  if (!res.ok) throw new Error('获取运行模式失败');
  return res.json();
}

export async function saveArticleHistory(payload: {
  article_id: string;
  title?: string;
  content?: string;
  change_type?: 'manual' | 'auto_save' | 'generation';
}) {
  const res = await fetch(`${API_BASE}/article-history/save`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('保存编辑历史失败');
  return res.json();
}

export async function getArticleHistory(articleId: string, limit: number = 20) {
  const res = await fetch(`${API_BASE}/article-history/${articleId}?limit=${limit}`);
  if (!res.ok) throw new Error('获取编辑历史失败');
  return res.json();
}

/** 流式请求大纲候选方案 */
export async function streamGenerateOutline(
  params: {
    category_id: string;
    template_id: string;
    input_type: string;
    topic: string;
    supplementary?: string;
    word_count: number;
    tone?: string;
    target_reader?: string;
  },
  onCandidate: (candidate: OutlineCandidate) => void,
  onStatus: (msg: string) => void,
  onDone: (articleId: string) => void,
  onError: (err: string) => void
) {
  try {
    const response = await fetch(`${API_BASE}/creation/generate-outline-stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });

    if (!response.ok || !response.body) {
      throw new Error(`HTTP 错误: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line.startsWith('event: candidate')) {
          const nextDataLine = lines[i + 1]?.trim();
          if (nextDataLine && nextDataLine.startsWith('data: ')) {
            const cand = JSON.parse(nextDataLine.replace('data: ', ''));
            onCandidate(cand);
            i++;
          }
        } else if (line.startsWith('event: status')) {
          const nextDataLine = lines[i + 1]?.trim();
          if (nextDataLine && nextDataLine.startsWith('data: ')) {
            const statusData = JSON.parse(nextDataLine.replace('data: ', ''));
            onStatus(statusData.message || '思考中...');
            i++;
          }
        } else if (line.startsWith('event: done')) {
          const nextDataLine = lines[i + 1]?.trim();
          if (nextDataLine && nextDataLine.startsWith('data: ')) {
            const doneData = JSON.parse(nextDataLine.replace('data: ', ''));
            onDone(doneData.article_id);
            i++;
          }
        }
      }
    }
  } catch (e: any) {
    onError(e.message || '生成失败');
  }
}

/** 流式请求生成全文正文 */
export async function streamGenerateArticle(
  params: {
    article_id: string;
    selected_title: string;
    confirmed_outline: string;
  },
  onChunk: (chunk: string) => void,
  onComplete: (data: { word_count: number; disclaimer?: string }) => void,
  onError: (err: string) => void
) {
  try {
    const response = await fetch(`${API_BASE}/creation/generate-article-stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });

    if (!response.ok || !response.body) {
      throw new Error(`HTTP 错误: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line.startsWith('event: chunk')) {
          const nextDataLine = lines[i + 1]?.trim();
          if (nextDataLine && nextDataLine.startsWith('data: ')) {
            const dataObj = JSON.parse(nextDataLine.replace('data: ', ''));
            onChunk(dataObj.content);
            i++;
          }
        } else if (line.startsWith('event: complete')) {
          const nextDataLine = lines[i + 1]?.trim();
          if (nextDataLine && nextDataLine.startsWith('data: ')) {
            const doneObj = JSON.parse(nextDataLine.replace('data: ', ''));
            onComplete(doneObj);
            i++;
          }
        }
      }
    }
  } catch (e: any) {
    onError(e.message || '全文生成失败');
  }
}
