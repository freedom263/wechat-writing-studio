from typing import Optional
from pydantic import BaseModel

class PromptConfigOut(BaseModel):
    id: str
    template_id: str
    prompt_type: str
    system_prompt: str
    user_prompt_template: str
    model_name: str
    temperature: float
    version: int
    is_active: bool
    append_disclaimer: bool
    disclaimer_text: Optional[str]

    class Config:
        from_attributes = True

class PromptConfigUpdate(BaseModel):
    system_prompt: Optional[str] = None
    user_prompt_template: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    append_disclaimer: Optional[bool] = None
    disclaimer_text: Optional[str] = None
