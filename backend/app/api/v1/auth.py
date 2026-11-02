import random
import string
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.core.database import get_db
from app.core.auth import create_access_token, get_current_user
from app.models.user import User, VerificationCode
from app.schemas.auth import (
    SendCodeRequest,
    VerifyCodeRequest,
    LoginResponse,
    UserInfo,
    UpdateProfileRequest
)

router = APIRouter(prefix="/auth", tags=["用户认证"])

def generate_code(length: int = 6) -> str:
    """生成随机验证码"""
    return ''.join(random.choices(string.digits, k=length))


@router.post("/send-code")
async def send_verification_code(payload: SendCodeRequest, db: AsyncSession = Depends(get_db)):
    """发送验证码（演示模式：直接返回验证码，生产环境应调用短信服务）"""
    code = generate_code()
    expires_at = datetime.utcnow() + timedelta(minutes=5)

    # 清理该手机号的旧验证码
    query = select(VerificationCode).where(
        VerificationCode.phone == payload.phone,
        VerificationCode.is_used == False
    )
    result = await db.execute(query)
    old_codes = result.scalars().all()
    for old_code in old_codes:
        old_code.is_used = True

    # 创建新验证码
    new_code = VerificationCode(
        phone=payload.phone,
        code=code,
        expires_at=expires_at
    )
    db.add(new_code)
    await db.commit()

    # 生产环境：调用短信服务发送验证码
    # await sms_service.send_code(payload.phone, code)

    # 演示模式：直接返回验证码
    return {
        "success": True,
        "message": "验证码已发送",
        "code": code,  # 仅演示模式返回，生产环境删除此行
        "expires_in": 300
    }


@router.post("/verify-code", response_model=LoginResponse)
async def verify_code_and_login(payload: VerifyCodeRequest, db: AsyncSession = Depends(get_db)):
    """验证验证码并登录"""
    # 查找有效的验证码
    query = select(VerificationCode).where(
        and_(
            VerificationCode.phone == payload.phone,
            VerificationCode.code == payload.code,
            VerificationCode.is_used == False,
            VerificationCode.expires_at > datetime.utcnow()
        )
    )
    result = await db.execute(query)
    verification = result.scalar_one_or_none()

    if not verification:
        raise HTTPException(status_code=400, detail="验证码无效或已过期")

    # 标记验证码为已使用
    verification.is_used = True

    # 查找或创建用户
    user_query = select(User).where(User.phone == payload.phone)
    user_result = await db.execute(user_query)
    user = user_result.scalar_one_or_none()

    if not user:
        user = User(
            phone=payload.phone,
            nickname=f"用户{payload.phone[-4:]}"
        )
        db.add(user)

    user.last_login_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)

    # 生成 JWT token
    access_token = create_access_token(data={"sub": user.id})

    return LoginResponse(
        access_token=access_token,
        user=UserInfo.from_orm(user)
    )


@router.get("/me", response_model=UserInfo)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return UserInfo.from_orm(current_user)


@router.put("/profile", response_model=UserInfo)
async def update_user_profile(
    payload: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新用户信息"""
    if payload.nickname is not None:
        current_user.nickname = payload.nickname
    if payload.avatar is not None:
        current_user.avatar = payload.avatar

    current_user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(current_user)

    return UserInfo.from_orm(current_user)
