from typing import Protocol, Optional

import requests


class Http(Protocol):
    def post(self,
             domain: str,
             endpoint: str,
             json_data: str | None = None,
             params: dict[str, str] | None = None,
             files: dict[str, bytes] | None = None) -> requests.Response:
        ...


class DatastoreWriter(Protocol):
    def commit_entity(self,
                      data: dict[str, str],
                      kind: str,
                      tx_id: str,
                      project_id: Optional[str] = None,
                      exclude_from_indexes: Optional[str] = None):
        ...


class PubsubPublisher(Protocol):
    def publish_message(self, topic_path: str, message: str, attributes: dict[str, str]) -> str:
        ...


class BucketReader(Protocol):
    def read(self,
             filename: str,
             bucket_name: str,
             sub_dir: Optional[str] = None,
             project_id: Optional[str] = None) -> bytes:
        ...
