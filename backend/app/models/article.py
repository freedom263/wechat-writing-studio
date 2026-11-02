from datetime import datetime
import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Article(Base):
    """文章与草稿表 (全生命周期记录)"""
    __tablename__ = "articles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), default="admin", index=True)  # 预留商用多用户隔离
    category_id = Column(String(50), nullable=True)
    template_id = Column(String(50), nullable=True)
    
    input_type = Column(String(20), default="topic")  # topic / url / material
    raw_input = Column(Text, nullable=True)           # 原始输入主题或外部URL
    input_options = Column(JSON, nullable=True)       # {"word_count": 1500, "tone": "...", "target_reader": "..."}
    
    selected_title = Column(String(255), nullable=True)
    outline_content = Column(Text, nullable=True)     # 选中的大纲骨架
    final_content = Column(Text, nullable=True)       # 生成的最终 Markdown 正文
    
    status = Column(String(30), default="draft")      # draft / outline_done / article_generating / completed
    word_count = Column(Integer, default=0)
    disclaimer = Column(Text, nullable=True)          # 附加的合规免责声明
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    candidates = relationship("OutlineCandidate", back_populates="article", cascade="all, delete-orphan", lazy="selectin")


class OutlineCandidate(Base):
    """AI 生成的 3 组差异化候选标题与大纲方案"""
    __tablename__ = "outline_candidates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String(36), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    candidate_index = Column(Integer, nullable=False) # 1, 2, 3
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)             # 核心立意亮点
    outline_json = Column(JSON, nullable=True)        # 结构化大纲章节数组
    tags = Column(JSON, nullable=True)                # 标签列表, 如: ["节气调理", "食疗方"]
    
    created_at = Column(DateTime, default=datetime.utcnow)

    article = relationship("Article", back_populates="candidates")
