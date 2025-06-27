from abc import ABC, abstractmethod


class Parser(ABC):
    @abstractmethod
    def extract_text(self, file: str) -> str:
        pass