import uuid

import pytest

from app.db.repository import UserRepository
from app.schemas.user import RegistrationForm, UserUpdateSchema
from app.utils.user import register_user, update_user


class TestFunctionUserDatabase:
    @pytest.mark.asyncio()
    async def test_get_user_by_username(
        self,
        client,
        user_sample,
        db_session
    ):
        user_repository = UserRepository()
        user = await user_repository.get_by_username(db_session, user_sample.username)
        assert user == user_sample

        user = await user_repository.get_by_username(db_session, 'not_exist')
        assert user is None

    @pytest.mark.asyncio()
    async def test_get_user_by_id(
        self,
        client,
        user_sample,
        db_session
    ):
        user_repository = UserRepository()
        user = await user_repository.get(db_session, user_sample.id)
        assert user == user_sample

        user = await user_repository.get(db_session, str(uuid.uuid4()))
        assert user is None

    @pytest.mark.asyncio()
    async def test_register_user(
        self,
        client,
        user_sample,
        db_session
    ):
        new_user = RegistrationForm(
            username='user2',
            password='password2',
            email='user@example.com'
        )
        verdict, message = await register_user(db_session, new_user)
        assert verdict
        assert message == "Successful registration!"

        new_user = RegistrationForm(
            username='user',
            password='password2',
            email='user@example.com'
        )
        verdict, message = await register_user(db_session, new_user)
        assert not verdict
        assert message == "Username already exists."

    @pytest.mark.asyncio()
    async def test_update_user(
        self,
        client,
        user_sample,
        db_session
    ):
        user = user_sample
        new_user = RegistrationForm(
            username='user2',
            password='password2',
            email='user@example.com'
        )
        verdict, message = await register_user(db_session, new_user)
        assert verdict
        assert message == "Successful registration!"

        new_user = UserUpdateSchema(username='user3')
        new_user, message = await update_user(db_session, user, new_user)
        assert new_user
        assert new_user.username == 'user3'
        assert message == "Successful update!"

        new_user = UserUpdateSchema(username='user2')
        new_user, message = await update_user(db_session, user, new_user)
        assert new_user is None
        assert message == "Username already exists."

    @pytest.mark.asyncio()
    async def test_delete_user(
        self,
        client,
        user_sample,
        db_session
    ):
        uuid = user_sample.id
        user_repository = UserRepository()
        await user_repository.remove(db_session, obj_id=uuid)
        user = await user_repository.get(db_session, uuid)
        assert user is None
