from abc import ABC, abstractmethod


class GcpBase(ABC):

    @abstractmethod
    def publish_message(self, message: str, tx_id: str, topic_path: str) -> str:
        pass

    @abstractmethod
    def read_bucket(self, file_name: str) -> bytes:
        pass

    @abstractmethod
    def datastore_write(self,
                        data: dict[str, str],
                        kind: str,
                        tx_id: str,
                        exclude_from_indexes: str):
        pass
