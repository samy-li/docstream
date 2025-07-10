from abc import ABC, abstractmethod

class FileStorage(ABC):
    @abstractmethod
    def save_file(self, filename: str, content: bytes) -> str:
        """
             Save a file to the configured storage system.

             Args:
                 filename (str): The object name to assign.
                 content (bytes): The file's binary content.

             Returns:
                 str: storage path
        """
        pass

class ParserClient(ABC):
    @abstractmethod
    def send_to_parser(self, file_url: str) -> str:
        """
               Send a saved file to parser-service.

               Args:
                   file_url (str): path to the file in storage.

               Returns:
                   str: Parser response payload.
        """
        pass