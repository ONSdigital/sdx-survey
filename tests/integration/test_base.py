import io
import json
import os
import unittest
import zipfile
from pathlib import Path
from unittest.mock import Mock

import requests
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sdx_base.errors.retryable import RetryableError
from sdx_base.models.pubsub import Message, Envelope
from sdx_base.run import run
from sdx_base.server.server import RouterConfig
from sdx_base.server.tx_id import txid_from_pubsub
from sdx_base.services.datastore import DatastoreService
from sdx_base.services.http import HttpService
from sdx_base.services.pubsub import PubsubService
from sdx_base.services.storage import StorageService

from app.definitions.context import Context
from app.definitions.decrypter import DecryptionBase
from app.definitions.submission import SurveySubmission
from app.dependencies import get_http_service, get_pubsub_service, get_storage_service, get_decryption_service, \
    get_datastore_service
from app.routes import router, unrecoverable_error_handler
from app.services import deliver
from app.services.deliver import ZIP_FILE, CONTEXT
from app.settings import Settings


def get_json(file_name: str) -> SurveySubmission:
    path = f'tests/data/{file_name}'
    with open(path) as f:
        data = json.load(f)

    return data


def read_zip(zip_bytes: bytes) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for name in zf.namelist():
            with zf.open(name) as file:
                content = file.read()
                result[name] = content

    return result


class MockSecretReader:

    _test_comment_key: str = "Pk_eTrrXIaiEv62A6w5qwerYCxR4060Xo1j5pJO_J2c="

    def get_secret(self, _project_id: str, secret_id: str) -> str:
        if secret_id == "sdx-comment-key":
            return self._test_comment_key
        return secret_id


class TestBase(unittest.TestCase):

    def setUp(self):
        os.environ["PROJECT_ID"] = "ons-sdx-sandbox"
        proj_root = Path(__file__).parent.parent.parent  # sdx-survey dir

        router_config = RouterConfig(router,
                                     tx_id_getter=txid_from_pubsub,
                                     on_unrecoverable_handler=unrecoverable_error_handler)
        app: FastAPI = run(Settings,
                           routers=[router_config],
                           proj_root=proj_root,
                           secret_reader=MockSecretReader(),
                           serve=lambda a, b: a
                           )
        self.client = TestClient(app)

        self.message: Message = {
            "attributes": {"objectId": "to be set in test"},
            "data": "",
            "message_id": "",
            "publish_time": ""
        }

        self.envelope: Envelope = {
            "message": self.message,
            "subscription": ""
        }

        # fake bytes returned from sdx-transformer and sdx-image
        self.pck_contents = b'pck contents'
        self.spp_contents = b'spp contents'
        self.image_contents = b'image contents'

        self.deliver_posted_files: dict[str, bytes] = {}
        self.deliver_posted_params: dict[str, str] = {}

        def post_side_effect(_domain: str,
                             endpoint: str,
                             _json_data: str | None = None,
                             params: dict[str, str] | None = None,
                             files: dict[str, bytes] | None = None) -> requests.Response:

            contents: bytes
            if endpoint == deliver.BUSINESS_ENDPOINT or endpoint == deliver.ADHOC_ENDPOINT:
                # calling deliver so capture the files and params
                self.deliver_posted_files.update(files)
                self.deliver_posted_params.update(params)
                contents = b''
            elif endpoint == "spp":
                contents = self.spp_contents
            elif endpoint == "image":
                contents = self.image_contents
            else:
                contents = self.pck_contents

            response = requests.Response()
            response.status_code = 200
            response._content = contents
            return response

        self.receipt_called: bool = False
        self.receipt: dict[str, str] = {}
        self.receipt_topic: str = ""

        def publish_side_effect(topic_path: str, message: str, attributes: dict[str, str]) -> str:
            self.receipt = json.loads(message)
            self.receipt_topic = topic_path
            self.receipt_called = True
            return ""

        self.mock_http = Mock(spec=HttpService)
        self.mock_http.post.side_effect = post_side_effect
        self.mock_storage = Mock(spec=StorageService)
        self.mock_storage.read.return_value = b'submission bytes'
        self.mock_decryptor = Mock(spec=DecryptionBase)
        self.mock_pubsub = Mock(spec=PubsubService)
        self.mock_pubsub.publish_message = publish_side_effect
        self.mock_datastore = Mock(spec=DatastoreService)

        app.dependency_overrides[get_storage_service] = lambda: self.mock_storage
        app.dependency_overrides[get_decryption_service] = lambda: self.mock_decryptor
        app.dependency_overrides[get_http_service] = lambda: self.mock_http
        app.dependency_overrides[get_pubsub_service] = lambda: self.mock_pubsub
        app.dependency_overrides[get_datastore_service] = lambda: self.mock_datastore
        self.app = app

    def set_survey_submission(self, tx_id: str, survey_submission: SurveySubmission):
        self.message["attributes"]["objectId"] = tx_id
        self.mock_decryptor.decrypt_survey.return_value = survey_submission

    def get_zip_contents(self) -> dict[str, bytes]:
        actual_zip_file = self.deliver_posted_files[ZIP_FILE]
        return read_zip(actual_zip_file)

    def get_context(self) -> Context:
        return json.loads(self.deliver_posted_params[CONTEXT])

    def get_receipt(self) -> dict[str, str]:
        return self.receipt

    def get_receipt_topic(self) -> str:
        return self.receipt_topic

    def was_receipt_called(self) -> bool:
        return self.receipt_called

    def simulate_retryable_error_on_post(self):
        def retryable_side_effect(domain: str,
                             endpoint: str,
                             json_data: str | None = None,
                             params: dict[str, str] | None = None,
                             files: dict[str, bytes] | None = None) -> requests.Response:
            raise RetryableError()

        self.mock_http.post.side_effect = retryable_side_effect

    def simulate_data_error_on_post(self):
        def data_side_effect(_domain: str,
                             endpoint: str,
                             _json_data: str | None = None,
                             params: dict[str, str] | None = None,
                             files: dict[str, bytes] | None = None) -> requests.Response:
            response = requests.Response()
            response.status_code = 400
            response._content = b""
            return response

        self.mock_http.post.side_effect = data_side_effect
