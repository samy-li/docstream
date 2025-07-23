import logging
import threading
from processing_service.app.entrypoints.processing_servicer import serve
from processing_service.app.routes.endpoints import create_instance

logger = logging.getLogger(__name__)


def launch_all():
    """Launch both gRPC and HTTP servers."""

    def run_grpc():
        try:
            serve()
        except Exception as e:
            logger.exception("gRPC server failed: %s", e)

    def run_http():
        try:
            create_instance()
        except Exception as e:
            logger.exception("HTTP server failed: %s", e)

    # Start gRPC in background thread
    grpc_thread = threading.Thread(target=run_grpc, name="gRPC-Server",
                                   daemon=True)
    grpc_thread.start()

    logger.info("Both gRPC and HTTP servers started")

    # Run FastAPI server in main thread
    run_http()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    launch_all()
