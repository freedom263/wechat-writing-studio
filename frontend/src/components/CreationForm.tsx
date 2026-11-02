import React, { useState, useEffect } from 'react';
import { Link2, Lightbulb, FileText, Sparkles, Loader2, Wand2, RefreshCw, CheckCircle2, ChevronRight, X } from 'lucide-react';
import { parseUrl, expandTopic } from '../api/client';
import { Template, Category } from '../types';
import { LoadingSkeleton } from './LoadingSkeleton';

interface CreationFormProps {
  selectedCategory: Category | null;
  selectedTemplate: Template | null;
  onGenerate: (data: {
    input_type: string;
    topic: string;
    supplementary: string;
    word_count: number;
    tone: string;
    target_reader: string;
  }) => void;
  isLoading: boolean;
  statusMessage: string;
}

const TEMPLATE_PRESETS: Record<string, {
  topic: string;
  supplementary: string;
  tone: string;
  target_reader: string;
  topicPlaceholder: string;
  suppPlaceholder: string;
}> = {
  // 1. 中医健康
  tcm_seasonal: {
    topic: '霜降节气老胃肠防寒调养指南',
    supplementary: '面向中老年人，介绍药食同源代茶饮方子，语言通俗亲切',
    tone: '专业且通俗 (推荐)',
    target_reader: '中老年人及养生关注者',
    topicPlaceholder: '例如：立冬将至，教你一套不生虚火的温补法',
    suppPlaceholder: '例如：强调体质差异，给出适宜食材搭配...'
  },
  tcm_syndrome: {
    topic: '总感觉乏力嗜睡、舌苔发白齿痕重？一文讲透脾虚湿盛',
    supplementary: '拆解脾虚湿盛的日常信号，给出简易体质自测与代茶饮调理',
    tone: '专业且通俗 (推荐)',
    target_reader: '普通大众读者',
    topicPlaceholder: '例如：为什么一吃生冷就肚子胀？中医教你辨清虚实',
    suppPlaceholder: '例如：用身体能感受的信号讲清病因...'
  },
  tcm_herb_point: {
    topic: '黄芪泡水虽好，但这3类体质千万别乱喝',
    supplementary: '强调单味药材的适用与禁忌人群，避免盲目跟风进补',
    tone: '专业且通俗 (推荐)',
    target_reader: '中老年人及养生关注者',
    topicPlaceholder: '例如：每天按揉足三里，脾胃悄悄变强健',
    suppPlaceholder: '例如：介绍穴位精准定位与按揉频次手法...'
  },
  tcm_clinical_case: {
    topic: '一位32岁白领因长期冰咖啡致胃黏膜损伤的门诊思考',
    supplementary: '以真实接诊案例开篇（隐去隐私），层层剖析病机，警示职场人群',
    tone: '温暖治愈',
    target_reader: '职场白领与青年',
    topicPlaceholder: '例如：门诊手记：那位因过度进补导致失眠的老大爷',
    suppPlaceholder: '例如：记录看诊思路与对读者的预防警示...'
  },
  tcm_myth_busting: {
    topic: '天天喝红豆薏米茶真的能祛湿吗？老中医师辟谣',
    supplementary: '客观拆解生薏米与炒薏米差异，揭秘寒湿越喝越重的陷阱',
    tone: '逻辑严谨',
    target_reader: '普通大众读者',
    topicPlaceholder: '例如：朋友圈疯传的排毒养颜方，到底有多伤阳气',
    suppPlaceholder: '例如：从中西医双重视角进行科学拆解...'
  },

  // 2. 读书书评
  book_deep_review: {
    topic: '《被讨厌的勇气》：如何在关系中践行课题分离、找回真正自我',
    supplementary: '结合当代青年人际内耗困境，谈如何建立边界、摆脱讨好型人格',
    tone: '逻辑严谨',
    target_reader: '职场白领与青年',
    topicPlaceholder: '例如：《纳瓦尔宝典》：普通人建立财富与幸福的底层逻辑',
    suppPlaceholder: '例如：系统梳理全书核心骨架，提炼3大认知破局点...'
  },
  book_golden_quote: {
    topic: '杨绛先生百岁感言：世界是自己的，与他人毫无关系',
    supplementary: '围绕金句深度延伸，探讨在浮躁时代如何坚守内心的秩序与松弛',
    tone: '温暖治愈',
    target_reader: '普通大众读者',
    topicPlaceholder: '例如：毛姆经典金句：满地都是六便士，他却抬头看见了月亮',
    suppPlaceholder: '例如：围绕金句展开人生哲理思考...'
  },
  book_character_analysis: {
    topic: '重读《活着》福贵：在苦难的底色里，什么是活着的真正力量',
    supplementary: '剖析人物命运波折与生命韧性，给当代读者带来精神力量',
    tone: '温暖治愈',
    target_reader: '青年读者与深度阅读者',
    topicPlaceholder: '例如：拆解《繁花》阿宝：时代的弄潮儿与命运的过客',
    suppPlaceholder: '例如：从人物性格切入分析时代命运...'
  },
  book_thematic_thinking: {
    topic: '从《工作、消费主义和新穷人》看当下年轻人的“隐形倦怠”',
    supplementary: '跳出个案看社会结构，讨论如何重塑个人劳动意义',
    tone: '逻辑严谨',
    target_reader: '职场白领与青年',
    topicPlaceholder: '例如：为什么我们越来越难拥有深度的亲密关系？',
    suppPlaceholder: '例如：跨界串联社会学与心理学经典著作...'
  },

  // 3. 职场成长
  wp_communication: {
    topic: '向上汇报的3个黄金法则：如何让领导一眼看懂你的核心价值',
    supplementary: '提供“结论先行+行动方案+备选决策”具体沟通话术模型',
    tone: '专业且通俗 (推荐)',
    target_reader: '职场白领与青年',
    topicPlaceholder: '例如：跨部门协作推不动？教你3招打破部门墙',
    suppPlaceholder: '例如：结构化话术拆解，附带可直接套用的模板...'
  },
  wp_promotion: {
    topic: '为什么埋头苦干的人往往很难升职？拆解优秀员工的破局思维',
    supplementary: '从战略对齐、影响力构建与资源统筹三个维度剖析职场天花板',
    tone: '专业且通俗 (推荐)',
    target_reader: '职场白领与青年',
    topicPlaceholder: '例如：工作5年如何完成从骨干到管理者的心智跃迁',
    suppPlaceholder: '例如：梳理晋升考核的核心考察点...'
  },

  // 4. 时事观点
  ca_hot_deep: {
    topic: '如何看待“情绪价值消费”在年轻群体中的全面爆发？',
    supplementary: '从社会心理学和新消费经济双重视角，理性客观探讨背后动因',
    tone: '逻辑严谨',
    target_reader: '普通大众读者',
    topicPlaceholder: '例如：AI 工具爆发背后，普通人应当如何构建护城河',
    suppPlaceholder: '例如：剥离情绪宣泄，直击事件背后的核心逻辑...'
  },
  ca_timeline: {
    topic: '从立项到出圈：完整复盘某现象级文旅出圈的底层密码',
    supplementary: '梳理关键事件节点、舆论引爆点与给其他城市的借鉴启示',
    tone: '专业且通俗 (推荐)',
    target_reader: '行业从业者',
    topicPlaceholder: '例如：按时间线复盘争议事件的前因后果与反转',
    suppPlaceholder: '例如：客观还原时间线，梳理各方利益诉求...'
  }
};

export const CreationForm: React.FC<CreationFormProps> = ({
  selectedCategory,
  selectedTemplate,
  onGenerate,
  isLoading,
  statusMessage
}) => {
  const [inputType, setInputType] = useState<'topic' | 'url' | 'material'>('topic');
  const [topic, setTopic] = useState('');
  const [url, setUrl] = useState('');
  const [supplementary, setSupplementary] = useState('');
  const [wordCount, setWordCount] = useState<number>(1500);
  const [tone, setTone] = useState('专业且通俗 (推荐)');
  const [targetReader, setTargetReader] = useState('普通大众读者');
  const [isParsingUrl, setIsParsingUrl] = useState(false);
  const [urlExtractNotice, setUrlExtractNotice] = useState('');

  // AI 意图理解与扩写状态
  const [isExpanding, setIsExpanding] = useState(false);
  const [expandSuggestions, setExpandSuggestions] = useState<Array<{ topic: string; supplementary: string }>>([]);
  const [expandBatch, setExpandBatch] = useState(1);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [adoptedIndex, setAdoptedIndex] = useState<number | null>(null);

  const currentPreset = selectedTemplate ? TEMPLATE_PRESETS[selectedTemplate.id] : null;

  // 切换模板联动预设
  useEffect(() => {
    if (selectedTemplate) {
      const preset = TEMPLATE_PRESETS[selectedTemplate.id];
      if (preset) {
        setTone(preset.tone);
        setTargetReader(preset.target_reader);
        setTopic(preset.topic);
        setSupplementary(preset.supplementary);
      } else {
        setTopic(`关于「${selectedTemplate.name}」的深度构思`);
        setSupplementary(`结合${selectedCategory?.name || '本赛道'}受众特点，展开逻辑严密的结构化撰写`);
      }
    }
  }, [selectedTemplate?.id]);

  const handleApplyPreset = () => {
    if (currentPreset) {
      setTopic(currentPreset.topic);
      setSupplementary(currentPreset.supplementary);
      setTone(currentPreset.tone);
      setTargetReader(currentPreset.target_reader);
    }
  };

  const handleClearInputs = () => {
    setTopic('');
    setSupplementary('');
    setShowSuggestions(false);
  };

  // AI 智能意图理解与构思扩写
  const handleAiExpand = async (batchNum: number = 1) => {
    if (!selectedTemplate || !selectedCategory) return;
    const keywordsToUse = topic.trim() || currentPreset?.topic || selectedTemplate.name;
    setIsExpanding(true);
    setAdoptedIndex(null);
    try {
      const res = await expandTopic({
        category_id: selectedCategory.id,
        template_id: selectedTemplate.id,
        keywords: keywordsToUse,
        tone,
        target_reader: targetReader,
        batch: batchNum
      });
      setExpandSuggestions(res.suggestions);
      setShowSuggestions(true);
      setExpandBatch(batchNum);
    } catch (e: any) {
      alert(`构思生成失败: ${e.message}`);
    } finally {
      setIsExpanding(false);
    }
  };

  // 换一换
  const handleShuffle = () => {
    handleAiExpand(expandBatch + 1);
  };

  // 采纳方案
  const handleAdoptSuggestion = (s: { topic: string; supplementary: string }, idx: number) => {
    setTopic(s.topic);
    setSupplementary(s.supplementary);
    setAdoptedIndex(idx);
    setTimeout(() => {
      setShowSuggestions(false);
      setAdoptedIndex(null);
    }, 600);
  };

  const handleParseUrl = async () => {
    if (!url.trim()) return;
    setIsParsingUrl(true);
    setUrlExtractNotice('');
    try {
      const data = await parseUrl(url.trim());
      setTopic(data.title);
      setSupplementary(`从外部链接提炼摘要：${data.summary}\n核心要点：${data.clean_content.slice(0, 300)}...`);
      setUrlExtractNotice(`已提取《${data.title}》并转化为创作主题！`);
    } catch (err: any) {
      alert(`提取失败: ${err.message}`);
    } finally {
      setIsParsingUrl(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) {
      alert('请输入文章创作主题');
      return;
    }
    onGenerate({
      input_type: inputType,
      topic: topic.trim(),
      supplementary: supplementary.trim(),
      word_count: wordCount,
      tone,
      target_reader: targetReader
    });
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
      <div className="p-4 space-y-3">
        {/* Top Header: Input Mode Selector + Actions */}
        <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
          <div className="flex space-x-1 bg-slate-100 p-0.5 rounded-lg text-xs">
            <button
              type="button"
              onClick={() => setInputType('topic')}
              className={`px-3 py-1 rounded-md font-semibold transition-smooth ${
                inputType === 'topic' ? 'bg-white text-blue-700 shadow-md' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              主题自由创作
            </button>
            <button
              type="button"
              onClick={() => setInputType('url')}
              className={`px-3 py-1 rounded-md font-semibold transition-smooth ${
                inputType === 'url' ? 'bg-white text-blue-700 shadow-md' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              文章链接转化
            </button>
            <button
              type="button"
              onClick={() => setInputType('material')}
              className={`px-3 py-1 rounded-md font-semibold transition-smooth ${
                inputType === 'material' ? 'bg-white text-blue-700 shadow-md' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              素材库提取
            </button>
          </div>

          <div className="flex items-center space-x-1.5">
            <button
              type="button"
              onClick={handleApplyPreset}
              className="text-[11px] text-blue-700 hover:bg-blue-50 px-2 py-0.5 rounded border border-blue-200 flex items-center space-x-1 font-medium transition-smooth hover-lift"
              title="载入本模板专属示例"
            >
              <Wand2 className="w-3 h-3 text-blue-600" />
              <span>填入示例</span>
            </button>
            <button
              type="button"
              onClick={handleClearInputs}
              className="text-[11px] text-slate-400 hover:text-slate-700 px-1.5 py-0.5 rounded hover:bg-slate-100 transition-smooth"
              title="清空主题与说明"
            >
              清空
            </button>
          </div>
        </div>

        {/* URL Input Mode */}
        {inputType === 'url' && (
          <div className="space-y-1.5 bg-slate-50 p-2.5 rounded-lg border border-slate-200">
            <label className="block text-[11px] font-semibold text-slate-700">粘贴公众号或网页链接</label>
            <div className="flex space-x-2">
              <input
                type="url"
                placeholder="https://mp.weixin.qq.com/s/..."
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="flex-1 bg-white border border-slate-300 rounded px-2.5 py-1 text-xs focus:ring-1 focus:ring-blue-500 focus:border-blue-500 focus:outline-none transition-smooth"
              />
              <button
                type="button"
                onClick={handleParseUrl}
                disabled={isParsingUrl || !url.trim()}
                className="px-3 py-1 bg-slate-900 hover:bg-slate-800 active:bg-slate-950 text-white rounded text-xs font-semibold shrink-0 flex items-center space-x-1 disabled:opacity-50 transition-smooth hover-lift"
              >
                {isParsingUrl ? <Loader2 className="w-3 h-3 animate-spin text-white" /> : null}
                <span>{isParsingUrl ? '提取中...' : '提取'}</span>
              </button>
            </div>
            {urlExtractNotice && (
              <p className="text-[10px] text-emerald-700 font-medium animate-fade-in">{urlExtractNotice}</p>
            )}
          </div>
        )}

        {/* Topic Input with AI Intent Expander & Shuffle */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-xs font-bold text-slate-800 flex items-center space-x-1">
              <span className="text-blue-600">*</span>
              <span>文章主题 / 核心痛点</span>
              {selectedTemplate && (
                <span className="text-[10px] text-slate-400 font-normal">
                  （{selectedTemplate.name}）
                </span>
              )}
            </label>
            <div className="flex items-center space-x-2">
              <button
                type="button"
                onClick={() => handleAiExpand(1)}
                disabled={isExpanding}
                className="text-[11px] text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 px-2 py-0.5 rounded flex items-center space-x-1 font-semibold transition-smooth disabled:opacity-50"
                title="输入零散关键词（如：立冬 萝卜），AI 自动理解意图扩展为专业标题与行文要求"
              >
                {isExpanding ? <Loader2 className="w-3 h-3 animate-spin" /> : <Sparkles className="w-3 h-3" />}
                <span>{isExpanding ? 'AI 构思中...' : 'AI 意图扩写'}</span>
              </button>
              <span className="text-[10px] text-slate-400">{topic.length}/100</span>
            </div>
          </div>
          <input
            type="text"
            value={topic}
            maxLength={100}
            onChange={(e) => setTopic(e.target.value)}
            placeholder={currentPreset?.topicPlaceholder || '输入零散关键词（如：立冬 萝卜）或完整主题...'}
            className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 text-xs text-slate-900 focus:bg-white focus:ring-1 focus:ring-blue-500 focus:border-blue-500 focus:outline-none transition-smooth"
          />

          {/* AI 意图理解扩写结果面板（包含换一换） */}
          {showSuggestions && (
            <div className="mt-2 p-2.5 bg-blue-50/70 border border-blue-200 rounded-xl space-y-2 animate-fade-in">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold text-blue-900 flex items-center space-x-1">
                  <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                  <span>AI 意图解析构思方案（点击卡片即可一键填入）：</span>
                </span>
                <div className="flex items-center space-x-2">
                  <button
                    type="button"
                    onClick={handleShuffle}
                    disabled={isExpanding}
                    className="text-[11px] text-blue-700 hover:text-blue-900 font-bold flex items-center space-x-1 hover:underline disabled:opacity-50"
                  >
                    <RefreshCw className={`w-3 h-3 ${isExpanding ? 'animate-spin' : ''}`} />
                    <span>换一换 (第 {expandBatch} 批)</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowSuggestions(false)}
                    className="text-slate-400 hover:text-slate-700"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              <div className="space-y-1.5">
                {expandSuggestions.map((item, idx) => (
                  <div
                    key={idx}
                    onClick={() => handleAdoptSuggestion(item, idx)}
                    className={`p-2 rounded-lg border bg-white cursor-pointer transition-smooth hover-lift flex items-start justify-between ${
                      adoptedIndex === idx
                        ? 'border-emerald-500 bg-emerald-50/40 ring-1 ring-emerald-500 shadow-md'
                        : 'border-slate-200 hover:border-blue-400 hover:shadow-md'
                    }`}
                  >
                    <div className="space-y-0.5 flex-1 pr-2">
                      <div className="text-xs font-bold text-slate-900 flex items-center space-x-1">
                        <span className="text-[10px] px-1 py-0.2 rounded bg-slate-100 text-slate-600 font-medium">方案{idx + 1}</span>
                        <span>{item.topic}</span>
                      </div>
                      <div className="text-[11px] text-slate-500 line-clamp-1 leading-relaxed">
                        {item.supplementary}
                      </div>
                    </div>
                    <div className="shrink-0 pt-0.5">
                      {adoptedIndex === idx ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-600 animate-fade-in" />
                      ) : (
                        <span className="text-[10px] text-blue-600 font-semibold flex items-center hover:underline">
                          采纳 <ChevronRight className="w-3 h-3" />
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Supplementary */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-xs font-bold text-slate-700">补充说明 / 行文要求 (选填)</label>
            <span className="text-[10px] text-slate-400">{supplementary.length}/300</span>
          </div>
          <textarea
            rows={2}
            maxLength={300}
            value={supplementary}
            onChange={(e) => setSupplementary(e.target.value)}
            placeholder={currentPreset?.suppPlaceholder || '例如：重点突出实操建议，语言逻辑严密...'}
            className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-xs text-slate-900 focus:bg-white focus:ring-1 focus:ring-blue-500 focus:border-blue-500 focus:outline-none transition-smooth resize-none"
          />
        </div>

        {/* Word Count Selector */}
        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1">
            <span className="text-blue-600 mr-1">*</span>预期正文字数
          </label>
          <div className="grid grid-cols-4 gap-2">
            {[
              { count: 800, desc: '简洁精炼' },
              { count: 1200, desc: '标准常用' },
              { count: 1500, desc: '内容充实' },
              { count: 2000, desc: '深度长文' }
            ].map((item) => (
              <button
                key={item.count}
                type="button"
                onClick={() => setWordCount(item.count)}
                className={`py-1.5 px-1 rounded-lg border text-center transition-smooth hover-lift ${
                  wordCount === item.count
                    ? 'border-blue-600 bg-blue-50/70 text-blue-900 font-bold ring-1 ring-blue-600 scale-105'
                    : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:shadow-md'
                }`}
              >
                <div className="text-xs font-bold">{item.count}字</div>
                <div className="text-[9px] text-slate-400">{item.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Tone & Reader settings */}
        <div className="grid grid-cols-2 gap-2 pt-0.5">
          <div>
            <label className="block text-[11px] font-medium text-slate-600 mb-0.5">行文风格</label>
            <select
              value={tone}
              onChange={(e) => setTone(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 rounded px-2 py-1 text-xs text-slate-700 focus:bg-white focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400 transition-smooth"
            >
              <option value="专业且通俗 (推荐)">专业且通俗 (推荐)</option>
              <option value="温暖治愈">温暖治愈</option>
              <option value="逻辑严谨">逻辑严谨</option>
              <option value="犀利深刻">犀利深刻</option>
              <option value="通俗科普">大白话通俗科普</option>
            </select>
          </div>
          <div>
            <label className="block text-[11px] font-medium text-slate-600 mb-0.5">目标读者</label>
            <select
              value={targetReader}
              onChange={(e) => setTargetReader(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 rounded px-2 py-1 text-xs text-slate-700 focus:bg-white focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400 transition-smooth"
            >
              <option value="普通大众读者">普通大众读者</option>
              <option value="中老年人及养生关注者">中老年人及养生关注者</option>
              <option value="职场白领与青年">职场白领与青年</option>
              <option value="青年读者与深度阅读者">青年读者与深度阅读者</option>
              <option value="行业从业者">行业从业者</option>
            </select>
          </div>
        </div>
      </div>

      {/* Sticky Bottom Action Bar with Guaranteed Solid High-Contrast Colors */}
      <div className="p-3 border-t border-slate-200 bg-slate-50/90 rounded-b-xl sticky bottom-0 z-10 backdrop-blur-xs">
        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-bold rounded-lg shadow-sm flex items-center justify-center space-x-2 transition-smooth hover-lift disabled:opacity-50 cursor-pointer"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin text-white" />
              <span className="text-xs text-white">{statusMessage || '正在构思大纲方案...'}</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4 text-white" />
              <span className="text-xs tracking-wider text-white">立即生成 3 组标题与大纲候选方案</span>
            </>
          )}
        </button>
      </div>
    </form>
  );
};
