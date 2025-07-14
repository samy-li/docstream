import grpc
from parser_service.app.proto import summarizer_pb2, summarizer_pb2_grpc


class SummarizerClient:
    def __init__(self, address: str = "localhost:50052", timeout: float = 5.0):
        self.address = address
        self.timeout = timeout
        self.channel = grpc.insecure_channel(self.address)
        self.stub = summarizer_pb2_grpc.SummarizerStub(self.channel)

    def summarize_and_store(self, request_id: str, text: str) -> bool:
        request = summarizer_pb2.SummaryJob(
            job_id=request_id,
            text=text
        )
        try:
            response = self.stub.Summarize(request, timeout=self.timeout)
            return response.success
        except grpc.RpcError as e:
            code = e.code()
            if code in [grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.DEADLINE_EXCEEDED]:
                raise RuntimeError(f"gRPC summarizer unavailable: {code}") from e
            else:
                # Non-retryable
                raise RuntimeError(f"gRPC summarization failed: {code}") from e

    def close(self):
        self.channel.close()
