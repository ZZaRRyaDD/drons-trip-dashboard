from os import environ
from uuid import uuid4

from app.config.default import DefaultSettings
from app.config.production import ProductionSettings


def get_settings() -> DefaultSettings:
    env = environ.get("ENV", "local")
    if env == "local":
        return DefaultSettings()
    if env == "test":
        # return TestSettings()
        return DefaultSettings(
            POSTGRES_DB="_".join(["pytest", uuid4().hex]),
        )
    if env == "prod":
        return ProductionSettings()
    return DefaultSettings()


settings = get_settings()
