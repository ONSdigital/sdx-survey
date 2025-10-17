from abc import ABC, abstractmethod
from typing import Self

from app.response import Response


class ProcessorBase(ABC):
    @abstractmethod
    def run(self: Self, response: Response):
        pass
