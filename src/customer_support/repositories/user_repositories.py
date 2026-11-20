from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.user_model import User
from ..services.security import verify_password

class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user: User) -> User:
        try:
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
        except SQLAlchemyError:
            await self.session.rollback()
            raise
        return user

    async def authenticate(self, user: User) -> User | None:
        try:
            res = await self.session.scalar(select(User).where(User.email == user.email))
            if res is None or not await verify_password(user.password_hash, res.password_hash):
                return None
            return res
        
        except SQLAlchemyError:
            await self.session.rollback()
            raise