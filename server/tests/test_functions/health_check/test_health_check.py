from app.utils.health_check import health_check_db


class TestFunctionHealthCheck:
    async def test_health_check_db(
        self,
        db_session
    ):
        health = await health_check_db(db_session)
        assert health
