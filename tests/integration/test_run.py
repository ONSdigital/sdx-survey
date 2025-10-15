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
from sdx_base.models.pubsub import Message, Envelope
from sdx_base.run import run
from sdx_base.server.server import RouterConfig
from sdx_base.server.tx_id import txid_from_pubsub
from sdx_base.services.datastore import DatastoreService
from sdx_base.services.http import HttpService
from sdx_base.services.pubsub import PubsubService
from sdx_base.services.storage import StorageService

from app.definitions.context import Context
from app.definitions.context_type import V2ContextType
from app.definitions.decrypter import DecryptionBase
from app.definitions.submission import SurveySubmission
from app.definitions.survey_type import SurveyType
from app.dependencies import get_http_service, get_pubsub_service, get_storage_service, get_decryption_service, \
    get_datastore_service
from app.routes import router
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


class TestRun(unittest.TestCase):

    def setUp(self):
        os.environ["PROJECT_ID"] = "ons-sdx-sandbox"
        proj_root = Path(__file__).parent.parent.parent  # sdx-survey dir

        router_config = RouterConfig(router, tx_id_getter=txid_from_pubsub)
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

        self.mock_storage = Mock(spec=StorageService)
        self.mock_storage.read.return_value = b'submission bytes'
        self.mock_decryptor = Mock(spec=DecryptionBase)
        self.mock_http = Mock(spec=HttpService)
        self.mock_http.post.side_effect = post_side_effect
        self.mock_pubsub = Mock(spec=PubsubService)
        self.mock_datastore = Mock(spec=DatastoreService)

        app.dependency_overrides[get_storage_service] = lambda: self.mock_storage
        app.dependency_overrides[get_decryption_service] = lambda: self.mock_decryptor
        app.dependency_overrides[get_http_service] = lambda: self.mock_http
        app.dependency_overrides[get_pubsub_service] = lambda: self.mock_pubsub
        app.dependency_overrides[get_datastore_service] = lambda: self.mock_datastore

    def test_mbs_legacy(self):
        submission_json = get_json("009.0106.json")
        tx_id = submission_json["tx_id"]
        self.message["attributes"]["objectId"] = tx_id
        self.mock_decryptor.decrypt_survey.return_value = submission_json

        resp = self.client.post("/", json=self.envelope)

        # expected files
        expected_pck_filename = '009_bddbb41275ea43ce'
        expected_image_filename = 'Sbddbb41275ea43ce_1.JPG'
        expected_index_filename = 'EDC_009_20230118_bddbb41275ea43ce.csv'
        expected_receipt_filename = 'REC1801_bddbb41275ea43ce.DAT'

        # actual files
        actual_zip_file = self.deliver_posted_files[ZIP_FILE]
        actual_files = read_zip(actual_zip_file)

        # expected context
        expected_context: Context = {
            "tx_id": tx_id,
            "survey_type": SurveyType.LEGACY,
            "context_type": V2ContextType.BUSINESS_SURVEY,
            "survey_id": "009",
            "period_id": "1605",
            "ru_ref": "12346789012A"
        }

        # actual context
        actual_context: Context = json.loads(self.deliver_posted_params[CONTEXT])

        self.assertTrue(resp.is_success)
        self.assertEqual(self.pck_contents, actual_files[expected_pck_filename])
        self.assertEqual(self.image_contents, actual_files[expected_image_filename])
        self.assertTrue(expected_index_filename in actual_files)
        self.assertTrue(expected_receipt_filename in actual_files)
        self.assertEqual(4, len(actual_files))
        self.assertEqual(expected_context, actual_context)

    def test_mbs_spp(self):
        submission_json = get_json("009.0106.json")
        submission_json["survey_metadata"]["period_id"] = "2512"
        tx_id = submission_json["tx_id"]
        self.message["attributes"]["objectId"] = tx_id
        self.mock_decryptor.decrypt_survey.return_value = submission_json

        resp = self.client.post("/", json=self.envelope)

        # expected files
        expected_spp_filename = '009_SDC_2023-01-18T13-33-19_bddbb412-75ea-43ce-9efa-0deb07cb8550.json'
        expected_image_filename = 'Sbddbb41275ea43ce_1.JPG'
        expected_index_filename = 'EDC_009_20230118_bddbb41275ea43ce.csv'
        expected_receipt_filename = 'REC1801_bddbb41275ea43ce.DAT'

        # actual files
        actual_zip_file = self.deliver_posted_files[ZIP_FILE]
        actual_files = read_zip(actual_zip_file)

        # expected context
        expected_context: Context = {
            "tx_id": tx_id,
            "survey_type": SurveyType.SPP,
            "context_type": V2ContextType.BUSINESS_SURVEY,
            "survey_id": "009",
            "period_id": "2512",
            "ru_ref": "12346789012A"
        }

        # actual context
        actual_context: Context = json.loads(self.deliver_posted_params[CONTEXT])

        self.assertTrue(resp.is_success)
        self.assertEqual(self.spp_contents, actual_files[expected_spp_filename])
        self.assertEqual(self.image_contents, actual_files[expected_image_filename])
        self.assertTrue(expected_index_filename in actual_files)
        self.assertTrue(expected_receipt_filename in actual_files)
        self.assertEqual(4, len(actual_files))
        self.assertEqual(expected_context, actual_context)

    def test_rsi_spp(self):
        submission_json = get_json("023.0102.json")
        tx_id = submission_json["tx_id"]
        self.message["attributes"]["objectId"] = tx_id
        self.mock_decryptor.decrypt_survey.return_value = submission_json

        resp = self.client.post("/", json=self.envelope)

        # expected files
        expected_spp_filename = '023_SDC_2016-03-12T13-01-26_11ed69f5-6c23-40cb-b4c2-70613bfe97fc.json'
        expected_image_filename = 'S11ed69f56c2340cb_1.JPG'
        expected_index_filename = 'EDC_023_20160312_11ed69f56c2340cb.csv'
        expected_receipt_filename = 'REC1203_11ed69f56c2340cb.DAT'

        # actual files
        actual_zip_file = self.deliver_posted_files[ZIP_FILE]
        actual_files = read_zip(actual_zip_file)

        # expected context
        expected_context: Context = {
            "tx_id": tx_id,
            "survey_type": SurveyType.SPP,
            "context_type": V2ContextType.BUSINESS_SURVEY,
            "survey_id": "023",
            "period_id": "1604",
            "ru_ref": "12345678901A"
        }

        # actual context
        actual_context: Context = json.loads(self.deliver_posted_params[CONTEXT])

        self.assertTrue(resp.is_success)
        self.assertEqual(self.spp_contents, actual_files[expected_spp_filename])
        self.assertEqual(self.image_contents, actual_files[expected_image_filename])
        self.assertTrue(expected_index_filename in actual_files)
        self.assertTrue(expected_receipt_filename in actual_files)
        self.assertEqual(4, len(actual_files))
        self.assertEqual(expected_context, actual_context)

    def test_adhoc(self):
        submission_json = get_json("740.0001.json")
        tx_id = submission_json["tx_id"]
        self.message["attributes"]["objectId"] = tx_id
        self.mock_decryptor.decrypt_survey.return_value = submission_json

        resp = self.client.post("/", json=self.envelope)

        # expected files
        expected_filename = 'cebf9e22-0b78-40d8-872d-ca5fe2507ab1.json'

        # actual files
        actual_zip_file = self.deliver_posted_files[ZIP_FILE]
        actual_files = read_zip(actual_zip_file)

        # expected context
        expected_context: Context = {
            "tx_id": tx_id,
            "survey_type": SurveyType.ADHOC,
            "context_type": V2ContextType.ADHOC_SURVEY,
            "survey_id": "740",
        }

        # actual context
        actual_context: Context = json.loads(self.deliver_posted_params[CONTEXT])

        self.assertTrue(resp.is_success)
        self.assertTrue(expected_filename in actual_files)
        self.assertEqual(1, len(actual_files))
        self.assertEqual(expected_context, actual_context)

    def test_dap(self):
        submission_json = get_json("283.0001.json")
        tx_id = submission_json["tx_id"]
        self.message["attributes"]["objectId"] = tx_id
        self.mock_decryptor.decrypt_survey.return_value = submission_json

        resp = self.client.post("/", json=self.envelope)

        # expected files
        expected_filename = 'c37a3efa-593c-4bab-b49c-bee0613c4fb4.json'

        # actual files
        actual_zip_file = self.deliver_posted_files[ZIP_FILE]
        actual_files = read_zip(actual_zip_file)

        # expected context
        expected_context: Context = {
            "tx_id": tx_id,
            "survey_type": SurveyType.DAP,
            "context_type": V2ContextType.BUSINESS_SURVEY,
            "survey_id": "283",
            'period_id': '201605',
            'ru_ref': '11842491738S',
        }

        # actual context
        actual_context: Context = json.loads(self.deliver_posted_params[CONTEXT])

        self.assertTrue(resp.is_success)
        self.assertTrue(expected_filename in actual_files)
        self.assertEqual(1, len(actual_files))
        self.assertEqual(expected_context, actual_context)

    def test_feedback(self):
        submission_json = get_json("139.0001.json")
        tx_id = submission_json["tx_id"]
        self.message["attributes"]["objectId"] = tx_id
        self.mock_decryptor.decrypt_survey.return_value = submission_json

        resp = self.client.post("/", json=self.envelope)

        # expected files
        expected_filename = 'cc7635a7-f204-4702-88a8-f1814e8d7295-fb-15-02-07_20-04-2021'

        # actual files
        actual_zip_file = self.deliver_posted_files[ZIP_FILE]
        actual_files = read_zip(actual_zip_file)

        # expected context
        expected_context: Context = {
            "tx_id": tx_id,
            "survey_type": SurveyType.FEEDBACK,
            "context_type": V2ContextType.BUSINESS_SURVEY,
            "survey_id": "139",
            'period_id': '1706',
            'ru_ref': '11110000002H',
        }

        # actual context
        actual_context: Context = json.loads(self.deliver_posted_params[CONTEXT])

        self.assertTrue(resp.is_success)
        self.assertTrue(expected_filename in actual_files)
        self.assertEqual(1, len(actual_files))
        self.assertEqual(expected_context, actual_context)
