from typing import Protocol

from sdx_base.services.datastore import commit_entity
from sdx_base.services.pubsub import PubsubService
from sdx_base.services.storage import StorageService

from app import get_logger
from app.definitions.gcp import GcpBase

logger = get_logger()


class GcpSettings(Protocol):
    project_id: str
    dap_topic_id: str

    def get_bucket_name(self) -> str: ...


class GcpService(GcpBase):

    def __init__(self, pubsub_service: PubsubService,
                 storage_service: StorageService,
                 settings: GcpSettings):
        self._pubsub_service = pubsub_service
        self._storage_service = storage_service
        self._settings = settings

    def publish_message(self, message: str, tx_id: str, topic_path: str) -> str:
        attributes = {
            'tx_id': tx_id
        }

        return self._pubsub_service.publish_message(topic_path, message, attributes)

    def read_bucket(self, file_name: str) -> bytes:
        bucket_name = self._settings.get_bucket_name()
        return self._storage_service.read(file_name, bucket_name=bucket_name, project_id=self._settings.project_id)

    def datastore_write(self,
                        data: dict[str, str],
                        kind: str,
                        tx_id: str,
                        exclude_from_indexes: str):

        commit_entity(data,
                      kind=kind,
                      tx_id=tx_id,
                      project_id=self._settings.project_id,
                      exclude_from_indexes=exclude_from_indexes)
