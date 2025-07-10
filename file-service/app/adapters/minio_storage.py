import logging
import io
from typing import Optional
from minio import Minio
from minio.error import S3Error
from tenacity import (retry, wait_exponential, stop_after_attempt,
                      retry_if_exception_type, before_sleep_log)

from app.interfaces.interfaces import FileStorage
from app.config.settings import get_settings

logger = logging.getLogger(__name__)


class MinIOStorage(FileStorage):
    """
    MinIO-based file storage system.
    """

    def __init__(self, client: Optional[Minio] = None,
                 bucket: Optional[str] = None):
        settings = get_settings()

        self.bucket: str = bucket or settings.minio_bucket
        self.client: Minio = client or Minio(
            endpoint=settings.minio_host,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )

        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(S3Error),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def save_file(self, filename: str, content: bytes) -> str:
        self.client.put_object(
            bucket_name=self.bucket,
            object_name=filename,
            data=io.BytesIO(content),
            length=len(content),
            content_type="application/octet-stream",
        )
        return f"s3://{self.bucket}/{filename}"
