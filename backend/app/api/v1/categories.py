from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryOut

router = APIRouter(prefix="/categories", tags=["赛道与模板"])

@router.get("", response_model=List[CategoryOut])
async def list_categories(db: AsyncSession = Depends(get_db)):
    """获取所有激活的赛道及其下的创作模板"""
    query = select(Category).where(Category.is_active == True).order_by(Category.sort_order)
    result = await db.execute(query)
    categories = result.scalars().all()
    return categories
