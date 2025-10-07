from abc import ABC, abstractmethod


class StorageClientInterface(ABC):
    @abstractmethod
    def save(self, request_id: str, summary: str) -> str:
        pass
