from abc import ABC, abstractmethod

from app.response import Response


class Transform(ABC):
    @abstractmethod
    def get_file_name(self, response: Response) -> str:
        pass

    @abstractmethod
    def get_file_content(self, response: Response) -> bytes:
        pass
