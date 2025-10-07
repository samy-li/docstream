from functools import lru_cache
from pydantic.v1 import BaseSettings

class Settings(BaseSettings):
    secret_key = "<KEY>"
    algorithm = "HS256"
    access_token_expire_minutes = 60


@lru_cache
def get_settings():
    return Settings()
