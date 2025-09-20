import pytest
from starlette import status


class TestAuthentication:
    @staticmethod
    def get_url() -> str:
        return "/api/v1/user/authentication"

    @pytest.mark.asyncio
    async def test_base_scenario(self, client, user_sample):
        data = {
            "username": user_sample.username,
            "password": "user-password",
        }
        response = await client.post(url=self.get_url(), data=data)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_bad_password(self, client, user_sample):
        data = {
            "username": user_sample.username,
            "password": "user-user",
        }
        response = await client.post(url=self.get_url(), data=data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_not_exist_user(self, client, user_sample):
        data = {
            "username": "user123",
            "password": "user-user",
        }
        response = await client.post(url=self.get_url(), data=data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_empty_username(self, client, user_sample):
        data = {
            "username": "",
            "password": "user-user",
        }
        response = await client.post(url=self.get_url(), data=data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_empty_password(self, client, user_sample):
        data = {
            "username": user_sample.username,
            "password": "",
        }
        response = await client.post(url=self.get_url(), data=data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
