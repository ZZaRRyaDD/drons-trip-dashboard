from datetime import timedelta

from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.config import get_settings
from app.db.connection import get_session
from app.db.models import User
from app.db.repository import UserRepository
from app.schemas.user import (
    RegistrationForm,
    RegistrationSuccess,
    Token,
    UserSchema,
    UserUpdateSchema,
)
from app.utils.user import (
    authenticate_user,
    create_access_token,
    get_current_user,
    register_user,
    update_user,
)

api_router = APIRouter(
    prefix="/user",
    tags=["User"],
)


@api_router.post(
    "/authentication",
    status_code=status.HTTP_200_OK,
    response_model=Token,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Could not validate credentials",
        },
    },
)
async def authentication(
    _: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "Bearer"}


@api_router.post(
    "/registration",
    status_code=status.HTTP_201_CREATED,
    response_model=RegistrationSuccess,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad parameters for registration",
        },
    },
)
async def registration(
    _: Request,
    registration_form: RegistrationForm = Body(...),
    session: AsyncSession = Depends(get_session),
)-> dict[str, str]:
    is_success, message = await register_user(session, registration_form)
    if is_success:
        return {"message": message}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message,
    )


@api_router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserSchema,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Could not validate credentials",
        },
    },
)
async def get_me(
    _: Request,
    current_user: User = Depends(get_current_user),
):
    return current_user


@api_router.patch(
    "/update",
    status_code=status.HTTP_200_OK,
    response_model=UserSchema,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad parameters for update",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Could not validate credentials",
        },
    },
)
async def update(
    _: Request,
    updated_user: UserUpdateSchema = Body(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    new_user, message = await update_user(
        session,
        current_user,
        updated_user,
    )
    if new_user:
        return new_user
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message,
    )


@api_router.delete(
    "/remove",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Could not validate credentials",
        },
    },
)
async def remove(
    _: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await UserRepository().remove(session, obj_id=current_user.id)
