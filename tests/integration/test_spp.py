import json
import os
import unittest
from pathlib import Path
from unittest.mock import Mock

import requests
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sdx_base.models.pubsub import Message, Envelope
from sdx_base.run import run
from sdx_base.server.server import RouterConfig
from sdx_base.server.tx_id import txid_from_pubsub
from sdx_base.services.datastore import DatastoreService
from sdx_base.services.http import HttpService
from sdx_base.services.pubsub import PubsubService
from sdx_base.services.storage import StorageService

from app.definitions.decrypter import DecryptionBase
from app.definitions.submission import SurveySubmission
from app.dependencies import get_http_service, get_pubsub_service, get_storage_service, get_decryption_service, \
    get_datastore_service
from app.routes import router
from app.settings import Settings


def get_json(file_name: str) -> SurveySubmission:
    path = f'tests/data/{file_name}'
    with open(path) as f:
        data = json.load(f)

    return data


class MockSecretReader:

    def get_secret(self, _project_id: str, secret_id: str) -> str:
        if secret_id == "sdx-comment-key":
            return "Pk_eTrrXIaiEv62A6w5wlrzYCxR4060Xo1j5pJO_J2c="
        return secret_id


class TestSpp(unittest.TestCase):

    def test_spp(self):
        os.environ["PROJECT_ID"] = "ons-sdx-sandbox"
        proj_root = Path(__file__).parent.parent.parent  # sdx-survey dir

        router_config = RouterConfig(router, tx_id_getter=txid_from_pubsub)
        app: FastAPI = run(Settings,
                           routers=[router_config],
                           proj_root=proj_root,
                           secret_reader=MockSecretReader(),
                           serve=lambda a, b: a
                           )
        client = TestClient(app)

        submission_json = get_json("023.0102.json")
        tx_id = submission_json["tx_id"]
        message: Message = {
            "attributes": {"objectId": tx_id},
            "data": "",
            "message_id": "",
            "publish_time": ""
        }

        envelope: Envelope = {
            "message": message,
            "subscription": ""
        }

        def post_side_effect(domain: str, endpoint: str, *args, **kwargs) -> requests.Response:
            contents: bytes
            if endpoint == "spp":
                contents = b'spp contents'
            elif endpoint == "image":
                contents = b'image contents'
            else:
                contents = b'pck contents'

            response = requests.Response()
            response.status_code = 200
            response._content = contents
            return response

        mock_storage = Mock(spec=StorageService)
        mock_storage.read.return_value = b'submission bytes'
        mock_decryptor = Mock(spec=DecryptionBase)
        mock_decryptor.decrypt_survey.return_value = submission_json
        mock_http = Mock(spec=HttpService)
        mock_http.post.side_effect = post_side_effect

        app.dependency_overrides[get_storage_service] = lambda: mock_storage
        app.dependency_overrides[get_decryption_service] = lambda: mock_decryptor
        app.dependency_overrides[get_http_service] = lambda: mock_http
        app.dependency_overrides[get_pubsub_service] = lambda: Mock(spec=PubsubService)
        app.dependency_overrides[get_datastore_service] = lambda: Mock(spec=DatastoreService)

        resp = client.post("/", json=envelope)

        self.assertTrue(resp.is_success)
