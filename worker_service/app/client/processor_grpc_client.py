import logging
import grpc
import tenacity

from worker_service.app.config.settings import get_settings
from worker_service.app.interfaces.procesor_client_interface import (
    ProcessorClientInterface,
    ProcessorRequest
)
from worker_service.app.proto import summarizer_pb2_grpc, summarizer_pb2

logger = logging.getLogger(__name__)
settings = get_settings()


class ProcessorClient(ProcessorClientInterface):
    """
    gRPC client for communicating with the processor service.
    """

    def __init__(self, address: str | None = None):
        """
        Initialize the ProcessorClient.

        Args:
            address (str | None): Optional gRPC server address. Defaults to
                                  settings.processor_grpc_address.
        """
        self.address = address or settings.processor_grpc_address
        self.channel = grpc.insecure_channel(self.address)
        self.stub = summarizer_pb2_grpc.SummarizerStub(self.channel)

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=10),
        stop=tenacity.stop_after_attempt(3),
        reraise=True
    )
    def process(self, request: ProcessorRequest) -> bool:
        """
        Send a processing request to the gRPC processor service.

        Args:
            request (ProcessorRequest): Pydantic model containing job_id and text.

        Returns:
            bool: True if processing was successful, False otherwise.

        Raises:
            RuntimeError: If the gRPC call fails after retries.
        """
        logger.info(
            f"Sending gRPC request to processor at {self.address} "
            f"for job_id={request.job_id}"
        )

        grpc_request = summarizer_pb2.SummarizeJob(
            job_id=request.job_id,
            text=request.text
        )

        try:
            response = self.stub.Summarize(grpc_request)
            logger.info(
                f"Received response for job_id={request.job_id}: success={response.success}"
            )
            return response.success
        except grpc.RpcError as e:
            logger.error(f"gRPC call failed for job_id={request.job_id}: {e}")
            raise RuntimeError(f"gRPC processor call failed: {e}") from e

    def close(self):
        """
        Close the gRPC channel.
        """
        logger.info("Closing gRPC channel")
        self.channel.close()
