import logging

import grpc
from pybreaker import CircuitBreakerError

from app.config.settings import get_settings
from app.grpc import parser_pb2, parser_pb2_grpc
from app.interfaces.interfaces import ParserClient
from app.resilience.factory.breaker_factory import parser_breaker


logger = logging.getLogger(__name__)

class GRPCClient(ParserClient):
    """
       gRPC-based parser client that sends file URLs
       to the external parser service.
       """

    def __init__(self, host: str = get_settings().grpc_server_host,
                 port: int = get_settings().grpc_server_port):
        """
               Initializes the gRPC channel and stub to the parser service.

               Args:
                   host (str): Hostname of the gRPC parser service.
                   port (int): Port of the gRPC parser service.
        """
        self.target = f"{host}:{port}"
        self.channel = grpc.insecure_channel(self.target)
        self.stub = parser_pb2_grpc.ResumeParserStub(self.channel)

    def send_to_parser(self, file_url: str) -> str:
        """
               Sends a file URL to the parser-service.

               Args:
                   file_url (str): path to the file.

               Returns:
                   str: The text content returned by the parser.
        """
        request = parser_pb2.ParseResumeRequest(file_url=file_url)

        try:
            # RungRPC call through the circuit breaker
            return parser_breaker.call(self._invoke_grpc, request)

        except CircuitBreakerError:
            # Circuit is OPEN → skip calling parser_service
            logger.warning(
                f"[CircuitBreaker] parser_service unavailable — skipping {file_url}")
            raise

        except grpc.RpcError as e:
            logger.error(f"gRPC communication error with parser_service: {e}")
            raise
    def _invoke_grpc(self, request):
        response = self.stub.ParseResume(request, timeout=30)
        return response.text

    def __del__(self):
        if hasattr(self, 'channel'):
            self.channel.close()
