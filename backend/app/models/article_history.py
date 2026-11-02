from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class ArticleHistory(Base):
    """文章编辑历史记录表"""
    __tablename__ = "article_histories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String(36), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)

    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    change_type = Column(String(20), default="manual")  # manual / auto_save / generation

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    article = relationship("Article", backref="edit_history")
