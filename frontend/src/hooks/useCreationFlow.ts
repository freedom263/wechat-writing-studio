import { useState } from 'react';
import { OutlineCandidate } from '../types';
import { streamGenerateOutline, streamGenerateArticle } from '../api/client';

export type CreationStage = 'input' | 'candidates' | 'editor';

export function useCreationFlow() {
  const [articleId, setArticleId] = useState<string>('');
  const [candidates, setCandidates] = useState<OutlineCandidate[]>([]);
  const [isLoadingOutline, setIsLoadingOutline] = useState(false);
  const [outlineStatusMsg, setOutlineStatusMsg] = useState('');

  const [currentTitle, setCurrentTitle] = useState('');
  const [articleContent, setArticleContent] = useState('');
  const [isStreamingArticle, setIsStreamingArticle] = useState(false);
  const [creationStage, setCreationStage] = useState<CreationStage>('input');

  const generateOutline = (
    categoryId: string,
    templateId: string,
    formData: {
      input_type: string;
      topic: string;
      supplementary: string;
      word_count: number;
      tone: string;
      target_reader: string;
    }
  ) => {
    setIsLoadingOutline(true);
    setCandidates([]);
    setOutlineStatusMsg('DeepSeek 大模型已启动，正在结合赛道调性构思大纲...');
    setCreationStage('candidates');

    streamGenerateOutline(
      {
        category_id: categoryId,
        template_id: templateId,
        ...formData
      },
      (candidate) => {
        setCandidates((prev) => [...prev, candidate]);
      },
      (status) => {
        setOutlineStatusMsg(status);
      },
      (newArticleId) => {
        setArticleId(newArticleId);
        setIsLoadingOutline(false);
      },
      (err) => {
        alert(`大纲生成中断: ${err}`);
        setIsLoadingOutline(false);
      }
    );
  };

  const confirmCandidate = (selectedCand: OutlineCandidate) => {
    if (!articleId) return;

    setCurrentTitle(selectedCand.title);
    setArticleContent('');
    setCreationStage('editor');
    setIsStreamingArticle(true);

    const outlineText = selectedCand.outline_sections
      ? selectedCand.outline_sections.join('\n')
      : selectedCand.summary;

    streamGenerateArticle(
      {
        article_id: articleId,
        selected_title: selectedCand.title,
        confirmed_outline: outlineText
      },
      (chunk) => {
        setArticleContent((prev) => prev + chunk);
      },
      () => {
        setIsStreamingArticle(false);
      },
      (err) => {
        alert(`全文生成失败: ${err}`);
        setIsStreamingArticle(false);
      }
    );
  };

  const resetFlow = () => {
    setCreationStage('input');
    setCandidates([]);
    setArticleId('');
    setCurrentTitle('');
    setArticleContent('');
  };

  const loadArticle = (id: string, title: string, content: string) => {
    setArticleId(id);
    setCurrentTitle(title);
    setArticleContent(content);
    setCreationStage('editor');
  };

  return {
    articleId,
    candidates,
    isLoadingOutline,
    outlineStatusMsg,
    currentTitle,
    articleContent,
    isStreamingArticle,
    creationStage,
    generateOutline,
    confirmCandidate,
    resetFlow,
    loadArticle,
    setCreationStage
  };
}
