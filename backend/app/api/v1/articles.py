from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.auth import get_current_user_optional
from app.models.user import User
from app.models.article import Article
from app.schemas.creation import ArticleDetailOut

router = APIRouter(prefix="/articles", tags=["文章与草稿箱管理"])

@router.get("", response_model=List[ArticleDetailOut])
async def list_articles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """获取当前用户的历史文章与草稿"""
    user_id = current_user.id if current_user else "anonymous"
    query = select(Article).where(Article.user_id == user_id).order_by(Article.created_at.desc())
    result = await db.execute(query)
    articles = result.scalars().all()
    return articles

@router.get("/{article_id}", response_model=ArticleDetailOut)
async def get_article(
    article_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """获取单篇文章详情 (包含3组候选大纲与最终正文)"""
    user_id = current_user.id if current_user else "anonymous"
    query = select(Article).where(Article.id == article_id, Article.user_id == user_id)
    result = await db.execute(query)
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在或无权访问")
    return article

@router.put("/{article_id}")
async def update_article_content(
    article_id: str,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """手动保存编辑后的正文或标题"""
    user_id = current_user.id if current_user else "anonymous"
    query = select(Article).where(Article.id == article_id, Article.user_id == user_id)
    result = await db.execute(query)
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在或无权访问")

    if "final_content" in payload:
        article.final_content = payload["final_content"]
        article.word_count = len(article.final_content.replace("\n", "").replace(" ", ""))
    if "selected_title" in payload:
        article.selected_title = payload["selected_title"]

    await db.commit()
    return {"message": "保存成功", "word_count": article.word_count}
