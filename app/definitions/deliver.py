from abc import ABC, abstractmethod

from app.definitions.context import Context


class DeliverBase(ABC):
    @abstractmethod
    def deliver_zip(self, tx_id: str, zipped_file: bytes, context: Context):
        pass
