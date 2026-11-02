import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "文思·微信公众号创作工作台"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # 数据库配置（Railway 自动注入 DATABASE_URL，支持 PostgreSQL 和 SQLite）
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./writing_studio.db")

    # Railway 的 PostgreSQL URL 格式转换（postgres:// → postgresql+asyncpg://）
    @property
    def database_url_converted(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url

    # DeepSeek 模型调用配置 (兼容 OpenAI 规范)
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEFAULT_MODEL: str = "deepseek-chat"

    # CORS 跨域允许源（生产环境从 FRONTEND_URL 读取）
    @property
    def cors_origins(self) -> List[str]:
        origins = [
            "http://localhost:5173",
            "http://localhost:3000",
            "http://localhost:4173",
        ]
        frontend_url = os.getenv("FRONTEND_URL", "")
        if frontend_url:
            origins.append(frontend_url)
            if frontend_url.startswith("https://"):
                origins.append(frontend_url.replace("https://", "http://"))
        if not frontend_url:
            origins.append("*")
        return origins

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
