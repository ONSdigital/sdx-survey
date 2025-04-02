from abc import ABC, abstractmethod

from app.response import Response


class TransformerBase(ABC):

    @abstractmethod
    def create_zip(self, response: Response) -> bytes:
        pass
