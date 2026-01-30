from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin
from app.models.user import User
from app.schemas.user import UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead])
async def list_users(session: AsyncSession = Depends(get_db), _: User = Depends(require_admin)) -> list[User]:
    result = await session.execute(select(User))
    return list(result.scalars().all())


@router.put("/{user_id}/role", response_model=UserRead)
async def update_role(
    user_id: int,
    role: str,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> User:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.role = role
    await session.commit()
    await session.refresh(user)
    return user
