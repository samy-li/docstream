import grpc

from app.config.settings import get_settings
from app.grpc import parser_pb2, parser_pb2_grpc
from app.interfaces.interfaces import ParserClient


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
        response = self.stub.ParseResume(request)
        return response.text
