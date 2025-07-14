from functools import lru_cache
from typing import Dict, List, Type
from pydantic.v1 import BaseSettings
from parser_service.app.parsers.parser import Parser
from parser_service.app.parsers.pdf_parser import PDFParser
from parser_service.app.parsers.docx_parser import DocxParser
from parser_service.app.parsers.txt_parser import TxtParser


class Settings(BaseSettings):
    # RabbitMQ
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_pass: str = "guest"

    exchange: str = "resumate_exchange"
    queue: str = "summary_jobs"
    routing_key: str = "summary_job"
    dlx: str = "resumate_dlx"
    dlq: str = "resumate_dlq"

    max_retries: int = 5
    summary_dir: str = "summaries"
    retry_delay: float = 2.0

    # Supported types
    supported_types: Dict[str, List[str]] = {
        "pdf": ["application/pdf"],
        "docx": ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
        "txt": ["text/plain"],
    }

    parser_map: Dict[str, Type[Parser]] = {
        "pdf": PDFParser,
        "docx": DocxParser,
        "txt": TxtParser,
    }

    class Config:
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
