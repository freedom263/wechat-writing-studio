from typing import List, Optional
from pydantic import BaseModel

class TemplateOut(BaseModel):
    id: str
    category_id: str
    name: str
    description: Optional[str] = None
    tag: Optional[str] = "通用"
    sort_order: int = 0

    class Config:
        from_attributes = True

class CategoryOut(BaseModel):
    id: str
    name: str
    icon: Optional[str] = "BookOpen"
    description: Optional[str] = None
    sort_order: int = 0
    templates: List[TemplateOut] = []

    class Config:
        from_attributes = True
