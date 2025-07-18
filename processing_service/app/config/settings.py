from functools import lru_cache
from pathlib import Path

from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    def __init__(
            __pydantic_self__,
            _env_file: Optional[DotenvType] = env_file_sentinel,
            _env_file_encoding: Optional[str] = None,
            _env_nested_delimiter: Optional[str] = None,
            _secrets_dir: Optional[StrPath] = None,
            **values: Any,
    ):
        super().__init__(_env_file, _env_file_encoding, _env_nested_delimiter,
                         _secrets_dir, values)
        __pydantic_self__.OPENAI_API_KEY = None
        __pydantic_self__.OPENAI_MAX_TOKENS = None
        __pydantic_self__.OPENAI_MODEL = None

    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    SUMMARY_DIR = BASE_DIR / "summaries"
    MODEL = "gpt-3.5-turbo"
    PROMPT_DIR = Path(__file__).parent / "prompts"


@lru_cache
def get_settings():
    return Settings()
