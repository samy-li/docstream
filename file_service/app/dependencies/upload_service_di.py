from app.adapters.minio_storage import MinIOStorage
from app.core.upload_service import UploadService
from app.grpc_client import GRPCClient


def get_upload_service() -> UploadService:
    """
        Dependency injection for UploadService

    Returns:
        UploadService
    """
    return UploadService(storage=MinIOStorage(), parser=GRPCClient())