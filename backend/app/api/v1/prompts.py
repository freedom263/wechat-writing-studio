from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.prompt_config import PromptConfig
from app.schemas.prompt import PromptConfigOut, PromptConfigUpdate

router = APIRouter(prefix="/prompts", tags=["提示词资产管理"])

@router.get("/{template_id}", response_model=List[PromptConfigOut])
async def get_template_prompts(template_id: str, db: AsyncSession = Depends(get_db)):
    """获取指定模板关联的提示词资产 (大纲及正文提示词)"""
    query = select(PromptConfig).where(
        PromptConfig.template_id == template_id,
        PromptConfig.is_active == True
    )
    result = await db.execute(query)
    prompts = result.scalars().all()
    return prompts

@router.put("/{prompt_id}", response_model=PromptConfigOut)
async def update_prompt_config(prompt_id: str, payload: PromptConfigUpdate, db: AsyncSession = Depends(get_db)):
    """修改提示词资产并即时生效 (实现动态调优)"""
    query = select(PromptConfig).where(PromptConfig.id == prompt_id)
    result = await db.execute(query)
    prompt = result.scalar_one_or_none()
    if not prompt:
        raise HTTPException(status_code=404, detail="未找到对应提示词配置")
    
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(prompt, key, value)
    
    prompt.version += 1
    await db.commit()
    await db.refresh(prompt)
    return prompt
