from datetime import datetime
import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class PromptConfig(Base):
    """提示词资产表 (解决Prompt散落、无法热更新与版本控制痛点)"""
    __tablename__ = "prompt_configs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    template_id = Column(String(50), ForeignKey("templates.id", ondelete="CASCADE"), nullable=False, index=True)
    prompt_type = Column(String(30), nullable=False)  # 'outline' (大纲候选) 或 'article' (全文正文)
    
    system_prompt = Column(Text, nullable=False)
    user_prompt_template = Column(Text, nullable=False)  # 支持 {topic}, {word_count}, {tone}, {outline} 插槽
    
    model_name = Column(String(50), default="deepseek-chat")
    temperature = Column(Float, default=0.7)
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    
    # 医疗科普专属合规护栏
    append_disclaimer = Column(Boolean, default=False)
    disclaimer_text = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    template = relationship("Template", back_populates="prompts")
