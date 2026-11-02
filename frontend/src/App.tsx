import React, { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { TrackBar } from './components/TrackBar';
import { TemplateGrid } from './components/TemplateGrid';
import { CreationForm } from './components/CreationForm';
import { CandidatesView } from './components/CandidatesView';
import { ArticleEditor } from './components/ArticleEditor';
import { PromptModal } from './components/PromptModal';
import { ApiKeyModal } from './components/ApiKeyModal';
import { DraftsView } from './components/DraftsView';
import { PromptManagerView } from './components/PromptManagerView';
import { Template, Article } from './types';
import { useCategorySelection } from './hooks/useCategorySelection';
import { useCreationFlow } from './hooks/useCreationFlow';

export function App() {
  const [currentTab, setCurrentTab] = useState<'create' | 'drafts' | 'prompts'>('create');
  const [selectedAccount, setSelectedAccount] = useState('知行笔记');

  const {
    categories,
    selectedCategoryId,
    selectedTemplate,
    currentCategory,
    selectCategory,
    setSelectedTemplate
  } = useCategorySelection();

  const {
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
  } = useCreationFlow();

  const [promptModalTemplate, setPromptModalTemplate] = useState<Template | null>(null);
  const [isApiKeyModalOpen, setIsApiKeyModalOpen] = useState(false);

  const handleSelectCategory = (catId: string) => {
    selectCategory(catId);
    if (creationStage === 'candidates') {
      setCreationStage('input');
    }
  };

  const handleGenerateOutline = (formData: {
    input_type: string;
    topic: string;
    supplementary: string;
    word_count: number;
    tone: string;
    target_reader: string;
  }) => {
    if (!selectedTemplate) {
      alert('请先选择一个写作模板');
      return;
    }
    generateOutline(selectedCategoryId, selectedTemplate.id, formData);
  };

  const handleRestoreFromDraft = (art: Article) => {
    loadArticle(
      art.id,
      art.selected_title || art.raw_input || '未命名文章',
      art.final_content || ''
    );
    setCurrentTab('create');
  };

  return (
    <div className="flex h-screen overflow-hidden bg-[#f9fafb]">
      {/* Left Sidebar */}
      <Sidebar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        selectedAccount={selectedAccount}
        setSelectedAccount={setSelectedAccount}
        onOpenApiKeyModal={() => setIsApiKeyModalOpen(true)}
      />

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {currentTab === 'drafts' && (
          <DraftsView onSelectArticle={handleRestoreFromDraft} />
        )}

        {currentTab === 'prompts' && (
          <PromptManagerView />
        )}

        {currentTab === 'create' && (
          <div className="flex-1 flex flex-col">
            {/* Top 11 Track Selector Bar */}
            <TrackBar
              categories={categories}
              selectedCategoryId={selectedCategoryId}
              onSelectCategory={handleSelectCategory}
            />

            {/* Main Stage Content */}
            <div className="p-6 max-w-6xl mx-auto w-full space-y-6">
              {/* Header Title & Slogan */}
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-extrabold text-slate-900 tracking-tight flex items-center space-x-2">
                    <span>{currentCategory?.name || '开始创作'}</span>
                    <span className="text-xs px-2.5 py-0.5 rounded-md bg-slate-100 text-slate-700 font-semibold border border-slate-200">
                      当前赛道
                    </span>
                  </h2>
                  <p className="text-xs text-slate-500 mt-1">
                    {currentCategory?.description || '从一个灵感开始，创作一篇打动读者的深度公众号文章'}
                  </p>
                </div>
              </div>

              {/* Step 1 & 2: Template Selection and Creation Settings (Dual Column Layout) */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
                {/* Left 6 Cols: Template Selector */}
                <div className="lg:col-span-6">
                  <TemplateGrid
                    templates={currentCategory?.templates || []}
                    selectedTemplateId={selectedTemplate?.id || ''}
                    onSelectTemplate={setSelectedTemplate}
                    onOpenPromptModal={(tpl) => setPromptModalTemplate(tpl)}
                  />
                </div>

                {/* Right 6 Cols: Creation Settings Form */}
                <div className="lg:col-span-6">
                  <CreationForm
                    selectedCategory={currentCategory || null}
                    selectedTemplate={selectedTemplate}
                    onGenerate={handleGenerateOutline}
                    isLoading={isLoadingOutline}
                    statusMessage={outlineStatusMsg}
                  />
                </div>
              </div>

              {/* Step 3: Candidates View (Rendered once outline is generated) */}
              {creationStage === 'candidates' && candidates.length > 0 && (
                <div className="animate-fade-in pt-2">
                  <CandidatesView
                    candidates={candidates}
                    onConfirmGenerateArticle={handleConfirmCandidate}
                    isGeneratingArticle={isStreamingArticle}
                  />
                </div>
              )}

              {/* Step 4: Article Editor & WeChat Preview (Rendered when writing full article) */}
              {creationStage === 'editor' && (
                <div className="animate-fade-in pt-2">
                  <ArticleEditor
                    articleId={articleId}
                    initialTitle={currentTitle}
                    initialContent={articleContent}
                    isStreaming={isStreamingArticle}
                    authorName={selectedAccount}
                    onReset={() => setCreationStage('input')}
                  />
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Prompt Configuration Modal */}
      {promptModalTemplate && (
        <PromptModal
          template={promptModalTemplate}
          onClose={() => setPromptModalTemplate(null)}
        />
      )}

      {/* DeepSeek API Key Configuration Modal */}
      <ApiKeyModal
        isOpen={isApiKeyModalOpen}
        onClose={() => setIsApiKeyModalOpen(false)}
        onSuccess={() => setIsApiKeyModalOpen(false)}
      />
    </div>
  );
}

export default App;
