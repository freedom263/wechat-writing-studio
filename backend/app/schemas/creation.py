from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ParseUrlRequest(BaseModel):
    url: str = Field(..., description="外部文章链接")

class ParseUrlResponse(BaseModel):
    title: str
    clean_content: str
    summary: str

class GenerateOutlineRequest(BaseModel):
    category_id: str
    template_id: str
    input_type: str = "topic" # topic / url / material
    topic: str
    supplementary: Optional[str] = ""
    word_count: int = 1500
    tone: Optional[str] = "专业通俗"
    target_reader: Optional[str] = "大众读者"
    language_style: Optional[str] = "清晰流畅"
    professionalism: Optional[str] = "适中"
    formatting: Optional[str] = "标准排版"
    custom_requirements: Optional[str] = ""

class TopicSuggestion(BaseModel):
    topic: str
    supplementary: str

class ExpandTopicRequest(BaseModel):
    category_id: str
    template_id: str
    keywords: str = Field(..., description="用户输入的零散关键词或模糊想法")
    tone: Optional[str] = "专业且通俗 (推荐)"
    target_reader: Optional[str] = "普通大众读者"

class ExpandTopicResponse(BaseModel):
    suggestions: List[TopicSuggestion]

class OutlineCandidateOut(BaseModel):
    id: str
    candidate_index: int
    title: str
    summary: Optional[str] = ""
    tags: List[str] = []
    outline_json: Optional[Any] = None

    class Config:
        from_attributes = True

class GenerateArticleRequest(BaseModel):
    article_id: str
    selected_title: str
    confirmed_outline: str

class ArticleDetailOut(BaseModel):
    id: str
    category_id: Optional[str]
    template_id: Optional[str]
    input_type: str
    raw_input: Optional[str]
    input_options: Optional[Dict[str, Any]]
    selected_title: Optional[str]
    outline_content: Optional[str]
    final_content: Optional[str]
    status: str
    word_count: int
    disclaimer: Optional[str]
    candidates: List[OutlineCandidateOut] = []

    class Config:
        from_attributes = True
