from abc import ABC, abstractmethod

from app.response import Response


class TransformerBase(ABC):

    @abstractmethod
    def transform(self, response: Response) -> bytes:
        pass

