from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.repository import UserRepository
from app.schemas.user import RegistrationForm, UserUpdateSchema


async def register_user(
    session: AsyncSession,
    potential_user: RegistrationForm,
) -> tuple[bool, str]:
    try:
        await UserRepository().create(
            session,
            obj_in=potential_user.dict(exclude_unset=True, exclude_none=True),
        )
    except exc.IntegrityError:
        return False, "Username already exists."
    return True, "Successful registration!"


async def update_user(
    session: AsyncSession,
    current_user: User,
    updated_user: UserUpdateSchema,
) -> tuple[User | None, str]:
    new_user =  None
    try:
        new_user = await UserRepository().update(
            session=session,
            db_obj=current_user,
            obj_in=updated_user,
        )
    except (exc.IntegrityError, exc.PendingRollbackError):
        return new_user, "Username already exists."
    return new_user, "Successful update!"
