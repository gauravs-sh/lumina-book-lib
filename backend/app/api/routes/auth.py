from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def signup(payload: UserCreate, session: AsyncSession = Depends(get_db)) -> User:
    result = await session.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(email=payload.email, hashed_password=hash_password(payload.password), role=payload.role)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@router.post("/login", response_model=Token)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_db)) -> Token:
    result = await session.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(user.email)
    return Token(access_token=token)


@router.get("/profile", response_model=UserRead)
async def profile(user: User = Depends(get_current_user)) -> User:
    return user


@router.put("/profile", response_model=UserRead)
async def update_profile(
    payload: UserUpdate,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> User:
    if payload.email:
        result = await session.execute(select(User).where(User.email == payload.email, User.id != user.id))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        user.email = payload.email
    if payload.password:
        user.hashed_password = hash_password(payload.password)
    await session.commit()
    await session.refresh(user)
    return user


@router.post("/logout")
async def logout(_: User = Depends(get_current_user)) -> dict[str, str]:
    return {"detail": "Logged out"}
