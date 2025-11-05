from abc import ABC, abstractmethod

from app.response import Response


class CommentsBase(ABC):
    @abstractmethod
    def store_comments(self, response: Response):
        pass
