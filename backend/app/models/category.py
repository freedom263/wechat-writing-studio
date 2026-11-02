from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Category(Base):
    """内容赛道表 (如: 中医健康/医疗养生, 读书书评, 职场成长等)"""
    __tablename__ = "categories"

    id = Column(String(50), primary_key=True, index=True)  # 如: tcm_health, book_review
    name = Column(String(100), nullable=False)
    icon = Column(String(50), default="BookOpen")
    description = Column(String(255), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联模板
    templates = relationship("Template", back_populates="category", cascade="all, delete-orphan", lazy="selectin")


class Template(Base):
    """赛道细分模板表 (如: 时令节气调理, 深度书评, 故事叙事型等)"""
    __tablename__ = "templates"

    id = Column(String(50), primary_key=True, index=True)  # 如: tcm_seasonal, deep_review
    category_id = Column(String(50), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    tag = Column(String(50), default="通用")
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category", back_populates="templates")
    prompts = relationship("PromptConfig", back_populates="template", cascade="all, delete-orphan", lazy="selectin")
