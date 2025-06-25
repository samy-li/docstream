import grpc
import os
import parser_pb2, parser_pb2_grpc


STORAGE_DIR = "storage"

def send_file_to_parser(filename, storage_dir=STORAGE_DIR):
    file_path = os.path.join(storage_dir, filename)
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    channel = grpc.insecure_channel("localhost:50051")
    stub = parser_pb2_grpc.ResumeParserStub(channel)
    request = parser_pb2.ParseResumeRequest(filename=filename, file_content=file_bytes)
    response = stub.ParseResume(request)
    return response.text