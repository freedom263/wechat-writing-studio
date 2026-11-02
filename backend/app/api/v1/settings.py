import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.llm_service import llm_service
from app.core.config import settings

router = APIRouter(prefix="/settings", tags=["系统与大模型设置"])

class ApiKeyPayload(BaseModel):
    api_key: str

@router.get("/status")
async def get_settings_status():
    """获取当前大模型连接状态"""
    has_key = bool(settings.DEEPSEEK_API_KEY and settings.DEEPSEEK_API_KEY.strip())
    masked_key = ""
    if has_key:
        masked_key = settings.DEEPSEEK_API_KEY[:6] + "..." + settings.DEEPSEEK_API_KEY[-4:]
    return {
        "has_key": has_key,
        "masked_key": masked_key,
        "model": settings.DEFAULT_MODEL,
        "base_url": settings.DEEPSEEK_BASE_URL
    }

@router.get("/mode")
async def get_mode_info():
    """获取当前运行模式信息（演示模式 or 真实API模式）"""
    return llm_service.get_mode_info()

@router.post("/api-key")
async def update_api_key(payload: ApiKeyPayload):
    """在线更新 DeepSeek API Key 并热加载"""
    key = payload.api_key.strip()
    llm_service.update_api_key(key)

    # 尝试写回 .env 文件持久化
    try:
        env_path = "backend/.env"
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            with open(env_path, "w", encoding="utf-8") as f:
                replaced = False
                for line in lines:
                    if line.startswith("DEEPSEEK_API_KEY="):
                        f.write(f"DEEPSEEK_API_KEY={key}\n")
                        replaced = True
                    else:
                        f.write(line)
                if not replaced:
                    f.write(f"DEEPSEEK_API_KEY={key}\n")
    except Exception:
        pass

    return {
        "message": "DeepSeek API Key 设置成功，已即刻激活真实大模型引擎！",
        "has_key": bool(key)
    }
