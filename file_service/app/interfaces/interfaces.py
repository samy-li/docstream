from abc import ABC, abstractmethod

class FileStorage(ABC):
    @abstractmethod
    def save_file(self, filename: str, content: bytes) -> str:
        pass

class ParserClient(ABC):
    @abstractmethod
    def send_to_parser(self, file_name: str) -> str:
        pass