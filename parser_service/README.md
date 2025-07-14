# parser_service

`parser_service` is a gRPC microservice for extracting text from documents (PDF, DOCX, TXT).

## Features
- Parses `.pdf`, `.docx`, and `.txt` files
- Uses file extension + MIME type detection
- Fault-tolerant with custom error handling
- gRPC-based, modular architecture

## Run locally
python parser_service/app/server/parser_server.py

## Run with Docker
docker build -t parser_service .

docker run -p 50051:50051 parser_service

