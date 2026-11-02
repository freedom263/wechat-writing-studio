import json
import uuid
import re
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db, AsyncSessionLocal
from app.models.category import Category, Template
from app.models.prompt_config import PromptConfig
from app.models.article import Article, OutlineCandidate
from app.schemas.creation import (
    ParseUrlRequest,
    ParseUrlResponse,
    GenerateOutlineRequest,
    GenerateArticleRequest,
    ExpandTopicRequest,
    ExpandTopicResponse
)
from app.services.crawler_service import CrawlerService
from app.services.llm_service import llm_service

router = APIRouter(prefix="/creation", tags=["AI 智能创作流"])

def render_prompt_template(tpl: str, **kwargs) -> str:
    """安全渲染包含 JSON 结构花括号的 Prompt 模板"""
    rendered = tpl
    for k, v in kwargs.items():
        rendered = rendered.replace(f"{{{k}}}", str(v))
    return rendered

@router.post("/parse-url", response_model=ParseUrlResponse)
async def parse_url_content(payload: ParseUrlRequest):
    """解析微信公众号或外部网页链接的正文内容"""
    data = await CrawlerService.fetch_and_clean_url(payload.url)
    return data

@router.post("/expand-topic", response_model=ExpandTopicResponse)
async def expand_topic_from_keywords(payload: ExpandTopicRequest, batch: int = 1, db: AsyncSession = Depends(get_db)):
    """根据创作者输入的零散关键词，调用大模型意图理解，扩展为专业的主题与行文要求 (支持换一换)"""
    # 查找赛道与模板名称
    cat_query = select(Category).where(Category.id == payload.category_id)
    cat_res = await db.execute(cat_query)
    category = cat_res.scalar_one_or_none()
    cat_name = category.name if category else "通用赛道"

    tpl_query = select(Template).where(Template.id == payload.template_id)
    tpl_res = await db.execute(tpl_query)
    template = tpl_res.scalar_one_or_none()
    tpl_name = template.name if template else "通用模板"

    suggestions = await llm_service.expand_keywords_to_topics(
        keywords=payload.keywords,
        category_name=cat_name,
        template_name=tpl_name,
        tone=payload.tone or "专业且通俗",
        target_reader=payload.target_reader or "普通大众读者",
        batch=batch
    )
    return {"suggestions": suggestions}

@router.post("/generate-outline-stream")
async def generate_outline_stream(payload: GenerateOutlineRequest, db: AsyncSession = Depends(get_db)):
    """流式生成 3 组候选标题与结构大纲 (SSE)"""
    # 1. 查找对应模板的 Prompt 配置
    query = select(PromptConfig).where(
        PromptConfig.template_id == payload.template_id,
        PromptConfig.prompt_type == "outline",
        PromptConfig.is_active == True
    )
    result = await db.execute(query)
    prompt_config = result.scalar_one_or_none()
    
    # 兜底默认系统提示词
    sys_prompt = prompt_config.system_prompt if prompt_config else "你是一位资深微信公众号爆款创作者。"
    raw_user_tpl = prompt_config.user_prompt_template if prompt_config else (
        "请根据主题【{topic}】提供 3 组富有传播力的公众号标题与详细结构大纲。"
        "补充要求：{supplementary}，预期字数：{word_count}，风格：{tone}，读者：{target_reader}。"
        "请严格以 JSON 格式输出，包含 candidates: [{index, title, summary, tags, outline_sections}]。"
    )
    
    # 插槽渲染 (使用安全替换，避免干扰 Prompt 内部的 JSON 示例花括号)
    user_prompt = render_prompt_template(
        raw_user_tpl,
        topic=payload.topic,
        supplementary=payload.supplementary or "无额外补充",
        word_count=payload.word_count,
        tone=payload.tone or "专业通俗",
        target_reader=payload.target_reader or "大众读者"
    )

    # 预创建 Article 记录
    article_id = str(uuid.uuid4())
    new_article = Article(
        id=article_id,
        category_id=payload.category_id,
        template_id=payload.template_id,
        input_type=payload.input_type,
        raw_input=payload.topic,
        input_options={
            "word_count": payload.word_count,
            "tone": payload.tone,
            "target_reader": payload.target_reader
        },
        status="outline_generating"
    )
    db.add(new_article)
    await db.commit()

    async def sse_event_generator():
        # 阶段通知
        yield f"event: status\ndata: {json.dumps({'message': '正在分析主题与赛道调性...'}, ensure_ascii=False)}\n\n"
        
        full_content = ""
        async for chunk in llm_service.stream_chat_completion(
            system_prompt=sys_prompt,
            user_prompt=user_prompt,
            model=prompt_config.model_name if prompt_config else "deepseek-chat",
            temperature=prompt_config.temperature if prompt_config else 0.7
        ):
            full_content += chunk
            yield f"event: thinking\ndata: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
        
        # 尝试提取和解析 JSON
        candidates = []
        try:
            # 正则匹配 JSON 块
            json_match = re.search(r'\{[\s\S]*\}', full_content)
            if json_match:
                parsed = json.loads(json_match.group())
                candidates = parsed.get("candidates", [])
        except Exception:
            pass

        # 若解析失败，提供默认的 3 组保底
        if not candidates or len(candidates) < 1:
            candidates = [
                {
                    "index": 1,
                    "title": f"深入解读：关于「{payload.topic}」的核心思考",
                    "summary": "兼顾深度与实用价值的标准论述",
                    "tags": ["深度解析", "核心方法"],
                    "outline_sections": ["一、背景引言与现状问题", "二、核心病机与关键症结剖析", "三、落地应对法则与实操指引", "四、总结与展望"]
                },
                {
                    "index": 2,
                    "title": f"关于「{payload.topic}」，这3个误区很多人都踩过",
                    "summary": "从痛点误区切入，强吸引力与避坑指南",
                    "tags": ["避坑指南", "实操干货"],
                    "outline_sections": ["一、生活高频误区盘点", "二、为什么会产生这些误区", "三、科学权威的正确做法", "四、日常保健习惯养成"]
                },
                {
                    "index": 3,
                    "title": f"普通人如何理解「{payload.topic}」？一份极简入门指南",
                    "summary": "通俗易懂的极简指南，适合广泛转发",
                    "tags": ["通俗科普", "行动清单"],
                    "outline_sections": ["一、用生活大白话读懂核心要义", "二、体质或认知自查两步法", "三、循序渐进的改善清单", "四、给读者的暖心寄语"]
                }
            ]

        # 异步独立会话入库保存候选方案
        async with AsyncSessionLocal() as session:
            for item in candidates:
                cand = OutlineCandidate(
                    article_id=article_id,
                    candidate_index=item.get("index", 1),
                    title=item.get("title", ""),
                    summary=item.get("summary", ""),
                    tags=item.get("tags", []),
                    outline_json=item.get("outline_sections", [])
                )
                session.add(cand)
            
            # 更新文章状态
            query = select(Article).where(Article.id == article_id)
            res = await session.execute(query)
            art = res.scalar_one_or_none()
            if art:
                art.status = "outline_done"
            await session.commit()

        # 分别发送 3 组候选大纲
        for item in candidates:
            yield f"event: candidate\ndata: {json.dumps(item, ensure_ascii=False)}\n\n"
        
        # 发送完成事件
        yield f"event: done\ndata: {json.dumps({'article_id': article_id, 'candidate_count': len(candidates)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        sse_event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


@router.post("/generate-article-stream")
async def generate_article_stream(payload: GenerateArticleRequest, db: AsyncSession = Depends(get_db)):
    """基于选定的大纲流式生成长文全文正文 (SSE)"""
    # 1. 查找文章记录
    query = select(Article).where(Article.id == payload.article_id)
    result = await db.execute(query)
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 2. 查找全文 Prompt 配置
    prompt_query = select(PromptConfig).where(
        PromptConfig.template_id == article.template_id,
        PromptConfig.prompt_type == "article",
        PromptConfig.is_active == True
    )
    p_res = await db.execute(prompt_query)
    prompt_config = p_res.scalar_one_or_none()

    word_count_opt = article.input_options.get("word_count", 1500) if article.input_options else 1500
    sys_prompt = prompt_config.system_prompt if prompt_config else "你是一位精通微信公众号写作的专家创作者。"
    raw_user_tpl = prompt_config.user_prompt_template if prompt_config else (
        "请根据标题【{title}】以及大纲：\n{outline}\n展开撰写约 {word_count} 字的完整正文（Markdown 格式）。"
    )

    user_prompt = render_prompt_template(
        raw_user_tpl,
        title=payload.selected_title,
        outline=payload.confirmed_outline,
        word_count=word_count_opt
    )

    append_disclaimer = prompt_config.append_disclaimer if prompt_config else (article.category_id == "tcm_health")
    disclaimer_text = prompt_config.disclaimer_text if prompt_config and prompt_config.disclaimer_text else (
        "【健康提示】本文仅供医学常识与健康养生科普，不能替代临床诊疗。个人体质有异，如遇身体不适，请前往正规医疗机构遵医嘱就医。"
    )

    async def sse_article_generator():
        accumulated_content = ""
        async for chunk in llm_service.stream_chat_completion(
            system_prompt=sys_prompt,
            user_prompt=user_prompt,
            model=prompt_config.model_name if prompt_config else "deepseek-chat",
            temperature=prompt_config.temperature if prompt_config else 0.6
        ):
            accumulated_content += chunk
            yield f"event: chunk\ndata: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"

        # 若为医疗/健康赛道，自动挂载合规免责声明
        if append_disclaimer:
            disclaimer_block = f"\n\n---\n> **{disclaimer_text}**\n"
            accumulated_content += disclaimer_block
            yield f"event: chunk\ndata: {json.dumps({'content': disclaimer_block}, ensure_ascii=False)}\n\n"

        # 计算字数并保存
        char_count = len(accumulated_content.replace("\n", "").replace(" ", ""))
        async with AsyncSessionLocal() as session:
            art_q = select(Article).where(Article.id == payload.article_id)
            res = await session.execute(art_q)
            art = res.scalar_one_or_none()
            if art:
                art.selected_title = payload.selected_title
                art.outline_content = payload.confirmed_outline
                art.final_content = accumulated_content
                art.word_count = char_count
                art.disclaimer = disclaimer_text if append_disclaimer else None
                art.status = "completed"
                await session.commit()

        yield f"event: complete\ndata: {json.dumps({'article_id': payload.article_id, 'word_count': char_count, 'status': 'completed'}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        sse_article_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )
