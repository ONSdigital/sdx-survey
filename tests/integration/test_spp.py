import json
import os
import unittest
from pathlib import Path

from fastapi import FastAPI
from sdx_base.models.pubsub import Message
from sdx_base.run import run
from sdx_base.server.server import RouterConfig
from sdx_base.server.tx_id import txid_from_pubsub

from app.definitions.submission import SurveySubmission
from app.definitions.context_type import V2ContextType
from app.definitions.survey_type import SurveyType
from app.definitions.context import Context
from app.dependencies import get_http_service
from app.routes import router
from app.settings import Settings


def get_json(file_name: str) -> SurveySubmission:
    path = f'tests/data/{file_name}'
    with open(path) as f:
        data = json.load(f)

    return data


class MockSecretReader:

    def get_secret(self, _project_id: str, secret_id: str) -> str:
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

        app.dependency_overrides[get_http_service] = get_mock_encryptor
        app.dependency_overrides[get_pubsub_service] = get_mock_gcp
        app.dependency_overrides[get_storage_service] = get_mock_encryptor
        app.dependency_overrides[get_decryption_service] = get_mock_gcp


        survey_id = "023"
        submission_json = get_json("023.0102.json")
        tx_id = submission_json["tx_id"]
        message: Message = {
            "attributes": {"objectId": tx_id},
            "data": "",
            "message_id": "",
            "publish_time": ""
        }

        spp_contents = b'spp contents'
        image_contents = b'image contents'
        index_contents = b'index contents'
        zip_bytes = b'the zip bytes'

        submission: SurveySubmission = get_json("survey_v2_001")
        submission["tx_id"] = tx_id
        submission["survey_metadata"]["survey_id"] = survey_id
        submission["survey_metadata"]["period_id"] = period_id
        submission["survey_metadata"]["ru_ref"] = ru_ref

        mock_is_nifi_message.return_value = True
        mock_is_nifi_message_2.return_value = True
        mock_app.gcs_read.return_value = json.dumps(submission).encode()
        mock_decrypt.return_value = submission
        mock_spp.return_value = spp_contents
        mock_image.return_value = image_contents
        mock_index.return_value = index_contents
        mock_zip.return_value = zip_bytes

        process(self.message, tx_id)

        expected_files: dict[str, bytes] = {
            '009_SDC_2016-05-21T16-37-56_0f534ffc-9442-414c-b39f-a756b4adc6cb.json': spp_contents,
            'S0f534ffc9442414c_1.JPG': image_contents,
            'EDC_009_20160521_0f534ffc9442414c.csv': index_contents,
            'REC2105_0f534ffc9442414c.DAT': b'49900000001:A:009:202510'
        }

        mock_zip.assert_called_with(expected_files)

        expected_zip: bytes = zip_bytes
        expected_context: Context = {
            "tx_id": tx_id,
            "survey_id": survey_id,
            "ru_ref": ru_ref,
            "survey_type": SurveyType.SPP,
            "period_id": period_id,
            "context_type": V2ContextType.BUSINESS_SURVEY
        }

        mock_deliver.assert_called_with(tx_id, expected_zip, expected_context)
