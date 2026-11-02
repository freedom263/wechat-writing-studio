from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from app.core.database import get_db
from app.models.article_history import ArticleHistory
from app.models.article import Article
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/article-history", tags=["文章编辑历史"])

class SaveHistoryRequest(BaseModel):
    article_id: str
    title: str | None = None
    content: str | None = None
    change_type: str = "manual"  # manual / auto_save / generation

class HistoryResponse(BaseModel):
    id: str
    article_id: str
    title: str | None
    content: str | None
    change_type: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/save")
async def save_article_history(
    request: SaveHistoryRequest,
    db: AsyncSession = Depends(get_db)
):
    """保存文章编辑历史记录"""
    # 验证文章是否存在
    result = await db.execute(select(Article).where(Article.id == request.article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 创建历史记录
    history = ArticleHistory(
        article_id=request.article_id,
        title=request.title,
        content=request.content,
        change_type=request.change_type
    )
    db.add(history)
    await db.commit()
    await db.refresh(history)

    return {
        "message": "历史记录保存成功",
        "history_id": history.id,
        "created_at": history.created_at
    }

@router.get("/{article_id}", response_model=List[HistoryResponse])
async def get_article_history(
    article_id: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """获取文章的编辑历史记录"""
    result = await db.execute(
        select(ArticleHistory)
        .where(ArticleHistory.article_id == article_id)
        .order_by(desc(ArticleHistory.created_at))
        .limit(limit)
    )
    histories = result.scalars().all()
    return histories

@router.get("/{article_id}/count")
async def get_history_count(
    article_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取文章编辑历史记录数量"""
    result = await db.execute(
        select(ArticleHistory)
        .where(ArticleHistory.article_id == article_id)
    )
    count = len(result.scalars().all())
    return {"article_id": article_id, "history_count": count}
