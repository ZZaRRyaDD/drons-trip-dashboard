import pytest

from app.utils.user import authenticate_user, verify_password


class TestFunctionUserBL:
    @pytest.mark.asyncio()
    async def test_authenticate_user(
        self,
        client,
        user_sample,
        db_session
    ):
        user = await authenticate_user(
            session=db_session,
            username='not_exist',
            password='not_exist'
        )
        assert not user

        user = await authenticate_user(
            session=db_session,
            username='user',
            password='user-password'
        )
        assert user == user_sample

        user = await authenticate_user(
            session=db_session,
            username='user',
            password='bad-password'
        )
        assert not user
    
    @pytest.mark.asyncio()
    async def test_verify_password(
        self,
        client,
        user_sample,
    ):
        verified = verify_password('user-password', user_sample.password)
        assert verified

        verified = verify_password('bad-password', user_sample.password)
        assert not verified
