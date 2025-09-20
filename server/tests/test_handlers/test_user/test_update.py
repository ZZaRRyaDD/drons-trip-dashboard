import pytest
from starlette import status


class TestUpdate:
    @staticmethod
    def get_url() -> str:
        return "/api/v1/user/update"

    @staticmethod
    def get_auth_url() -> str:
        return "/api/v1/user/authentication"

    @staticmethod
    def get_register_url() -> str:
        return "/api/v1/user/registration"

    @pytest.mark.asyncio
    async def get_auth_token(self, client, data):
        response = await client.post(url=self.get_auth_url(), data=data)
        response = response.json()
        return response['access_token']

    @pytest.mark.asyncio
    async def test_base_scenario(self, client, user_sample):
        credentials = {
            "username": user_sample.username,
            "password": "user-password",
        }
        token = await self.get_auth_token(client, credentials)
        data = {
            "username": "some_user_name1",
        }
        response = await client.patch(
            url=self.get_url(),
            json=data,
            headers={"Authorization": f'Bearer {token}'}
        )
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_empty_username(self, client, user_sample):
        credentials = {
            "username": user_sample.username,
            "password": "user-password",
        }
        token = await self.get_auth_token(client, credentials)
        data = {
            "username": "",
        }
        response = await client.patch(
            url=self.get_url(),
            json=data,
            headers={"Authorization": f'Bearer {token}'}
        )
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_same_username(self, client, user_sample):
        data = {
            "username": "user1",
            "password": "user-password",
            "email": "user@example.com"
        }
        response = await client.post(url=self.get_register_url(), json=data)
        assert response.status_code == status.HTTP_201_CREATED

        credentials = {
            "username": user_sample.username,
            "password": "user-password",
        }
        token = await self.get_auth_token(client, credentials)
        data = {
            "username": "user1",
            "password": "user-password",
            "email": "user@example.com"
        }
        response = await client.patch(
            url=self.get_url(),
            json=data,
            headers={"Authorization": f'Bearer {token}'}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
