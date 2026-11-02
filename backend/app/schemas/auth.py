from typing import Optional
from pydantic import BaseModel, Field, validator
import re

class SendCodeRequest(BaseModel):
    phone: str = Field(..., description="手机号")

    @validator('phone')
    def validate_phone(cls, v):
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v


class VerifyCodeRequest(BaseModel):
    phone: str = Field(..., description="手机号")
    code: str = Field(..., description="验证码", min_length=6, max_length=6)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserInfo"


class UserInfo(BaseModel):
    id: str
    phone: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    nickname: Optional[str] = Field(None, max_length=100)
    avatar: Optional[str] = Field(None, max_length=500)
