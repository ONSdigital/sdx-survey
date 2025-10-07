from abc import ABC, abstractmethod


class GcpBase(ABC):

    @abstractmethod
    def publish_message(self, message: str, tx_id: str, topic_path: str) -> str:
        pass
