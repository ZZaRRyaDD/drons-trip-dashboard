import pytest

from app.config.utils import get_settings
from app.db.models import User


@pytest.fixture
async def user_sample(db_session) -> User:
    """
    Creates minimum user sample for tests.
    """
    settings = get_settings()
    new_object = User(
        username='user',
        password=settings.PWD_CONTEXT.hash("user-password"),
        email='user@example.com'
    )
    db_session.add(new_object)
    await db_session.commit()
    await db_session.refresh(new_object)
    return new_object
