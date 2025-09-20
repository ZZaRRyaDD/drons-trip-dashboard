from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserSchema(BaseModel):
    id: UUID
    username: str
    email: EmailStr | None

    model_config = ConfigDict(from_attributes=True)


class UserUpdateSchema(BaseModel):
    username: str | None = None
