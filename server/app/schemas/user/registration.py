from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, constr, field_validator

from app.config import get_settings


class RegistrationForm(BaseModel):
    username: str
    password: constr(min_length=8)
    email: EmailStr | None

    @field_validator("password")
    def validate_password(cls, password):
        if not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must not be empty string"
            )
        settings = get_settings()
        password = settings.PWD_CONTEXT.hash(password)
        return password

    @field_validator("username")
    def validate_username(cls, username):
        if not username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Username must not be empty string'
            )
        return username


class RegistrationSuccess(BaseModel):
    message: str
