from functools import lru_cache
from pathlib import Path

from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    SUMMARY_DIR = BASE_DIR / "summaries"


@lru_cache
def get_settings():
    return Settings()
