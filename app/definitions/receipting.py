from abc import ABC, abstractmethod

from app.response import Response


class ReceiptServiceBase(ABC):
    @abstractmethod
    def send_receipt(self, response: Response):
        pass
