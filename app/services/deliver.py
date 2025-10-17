import json
from typing import Final, Protocol

import requests

from app import get_logger
from app.definitions.context import Context
from app.definitions.context_type import ContextType
from app.definitions.deliver import DeliverBase

# Constants used within the http request
FILE_NAME: Final[str] = "filename"
ZIP_FILE: Final[str] = "zip_file"
CONTEXT: Final[str] = "context"
TX_ID: Final[str] = "tx_id"
BUSINESS_ENDPOINT: Final[str] = "deliver/v2/survey"
ADHOC_ENDPOINT: Final[str] = "deliver/v2/adhoc"

logger = get_logger()


class DeliverHttp(Protocol):
    def post(
        self,
        domain: str,
        endpoint: str,
        json_data: str | None = None,
        params: dict[str, str] | None = None,
        files: dict[str, bytes] | None = None,
    ) -> requests.Response: ...


class DeliverService(DeliverBase):
    def __init__(self, deliver_url: str, http_service: DeliverHttp):
        self._deliver_url = deliver_url
        self._http_service = http_service

    def deliver_zip(self, tx_id: str, zipped_file: bytes, context: Context):
        """
        Calls the sdx-deliver endpoint specified by the output_type parameter.
        Returns True or raises appropriate error on response.
        """

        # filename will always be transaction id
        filename: str = tx_id
        endpoint: str = BUSINESS_ENDPOINT
        if context["context_type"] == ContextType.ADHOC_SURVEY:
            endpoint = ADHOC_ENDPOINT

        context_json: str = json.dumps(context)

        self._http_service.post(
            self._deliver_url,
            endpoint,
            None,
            params={FILE_NAME: filename, TX_ID: tx_id, CONTEXT: context_json},
            files={ZIP_FILE: zipped_file},
        )
        return True
