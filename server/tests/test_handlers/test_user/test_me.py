import pytest
from starlette import status


class TestMe:
    @staticmethod
    def get_url() -> str:
        return "/api/v1/user/me"

    @staticmethod
    def get_auth_url() -> str:
        return "/api/v1/user/authentication"

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

        response = await client.get(
            url=self.get_url(),
            headers={"Authorization": f'Bearer {token}'}
        )
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_bad_token(self, client, user_sample):
        response = await client.get(
            url=self.get_url(),
            headers={"Authorization": 'Bearer some_token'}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
