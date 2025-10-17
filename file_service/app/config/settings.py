"""
 This file regroup file-service config values
"""
import logging
from functools import lru_cache
from typing import Set
from pydantic.v1 import BaseSettings, Field


logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # ------------------MinIO Configuration-------------------
    minio_host: str = Field(..., env="MINIO_HOST")
    minio_access_key: str = Field(..., env="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(..., env="MINIO_SECRET_KEY")
    minio_bucket: str = Field(..., env="MINIO_BUCKET")
    minio_secure: bool = Field(default=True, env="MINIO_SECURE")

    # ---------------------Upload Settings-----------------------
    max_file_size: int = Field(default=10 * 1024 * 1024,
                               env="MAX_FILE_SIZE",
                               gt=0)  # 10MB
    allowed_mime_types: Set[str] = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain"
    }

    # **************************** gRPC Server **********************
    grpc_server_host: str = Field(default="0.0.0.0", env="GRPC_SERVER_HOST")
    grpc_server_port: int = Field(default=50051, env="GRPC_SERVER_PORT")


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    try:
        settings = Settings()
        logger.info("Settings loaded successfully")
        return settings
    except Exception as e:
        logger.critical(f"Failed to load settings: {e}")
        raise
