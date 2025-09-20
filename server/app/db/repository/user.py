from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.schemas.user import RegistrationForm, UserUpdateSchema

from .base import BaseRepository


class UserRepository(BaseRepository[User, RegistrationForm, UserUpdateSchema]):
    def __init__(self):
        super().__init__(User)

    async def get_by_username(self, session: AsyncSession, username: str) -> User | None:
        query = select(User).where(User.username == username)
        return await session.scalar(query)
