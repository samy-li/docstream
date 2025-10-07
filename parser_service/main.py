import grpc
from concurrent import futures
from app.clients.server import DocumentParser
from app.proto import parser_pb2_grpc

def run():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    parser_pb2_grpc.add_ResumeParserServicer_to_server(DocumentParser(), server)
    server.add_insecure_port('[::]:50051')
    print("parser_service running on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    run()
