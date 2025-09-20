import pytest
from starlette import status


class TestHealthCheckHandler:
    @staticmethod
    def get_url() -> str:
        return "/api/v1/health_check"

    @pytest.mark.asyncio
    async def test_ping_application(self, client):
        url = self.get_url() + '/ping_application'
        response = await client.get(url=url)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio()
    async def test_ping_db(self, client):
        url = self.get_url() + '/ping_database'
        response = await client.get(url=url)
        assert response.status_code == status.HTTP_200_OK
