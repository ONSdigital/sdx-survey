import json
import unittest
from unittest.mock import patch, Mock

from sdx_gcp import Message

from app.survey import process
from app.definitions.submission import SurveySubmission
from app.definitions.context_type import V2ContextType
from app.definitions.survey_type import SurveyType
from app.definitions.context import Context
from tests import get_json


class TestMbs(unittest.TestCase):

    def setUp(self) -> None:
        self.message: Message = {
            "attributes": {"objectId": "0f534ffc-9442-414c-b39f-a756b4adc6cb"},
            "data": "",
            "message_id": "",
            "publish_time": ""
        }

    @patch('app.collect.sdx_app')
    @patch('app.collect.decrypt_survey')
    @patch('app.v2.processor_v2.store_comments')
    @patch('app.v2.processor_v2.send_receipt')
    @patch('app.transformation.transforms.PCK.get_contents')
    @patch('app.transformation.transforms.image.get_image')
    @patch('app.transformation.transforms.index.get_contents')
    @patch('app.transformation.transformers.create_zip')
    @patch('app.v2.processor_v2.deliver_zip')
    @patch('app.collect.is_v2_nifi_message_submission')
    @patch('app.transformation.create.is_v2_nifi_message_submission')
    def test_legacy(self,
                    mock_is_nifi_message: Mock,
                    mock_is_nifi_message_2: Mock,
                    mock_deliver: Mock,
                    mock_zip: Mock,
                    mock_index: Mock,
                    mock_image: Mock,
                    mock_pck: Mock,
                    _mock_receipt: Mock,
                    _mock_comments: Mock,
                    mock_decrypt: Mock,
                    mock_app: Mock):
        tx_id = '0f534ffc-9442-414c-b39f-a756b4adc6cb'
        survey_id = "009"
        period_id = "2504"
        ru_ref = "49900000001A"
        pck_contents = b'PCK contents'
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
        mock_pck.return_value = pck_contents
        mock_image.return_value = image_contents
        mock_index.return_value = index_contents
        mock_zip.return_value = zip_bytes

        process(self.message, tx_id)

        expected_files: dict[str, bytes] = {
            '009_0f534ffc9442414c': pck_contents,
            'S0f534ffc9442414c_1.JPG': image_contents,
            'EDC_009_20160521_0f534ffc9442414c.csv': index_contents,
            'REC2105_0f534ffc9442414c.DAT': b'49900000001:A:009:202504'
        }

        mock_zip.assert_called_with(expected_files)

        expected_zip: bytes = zip_bytes
        expected_context: Context = {
            "tx_id": tx_id,
            "survey_id": survey_id,
            "ru_ref": ru_ref,
            "survey_type": SurveyType.LEGACY,
            "period_id": period_id,
            "context_type": V2ContextType.BUSINESS_SURVEY
        }

        mock_deliver.assert_called_with(tx_id, expected_zip, expected_context)

    @patch('app.collect.sdx_app')
    @patch('app.collect.decrypt_survey')
    @patch('app.v2.processor_v2.store_comments')
    @patch('app.v2.processor_v2.send_receipt')
    @patch('app.transformation.transforms.spp.get_contents')
    @patch('app.transformation.transforms.image.get_image')
    @patch('app.transformation.transforms.index.get_contents')
    @patch('app.transformation.transformers.create_zip')
    @patch('app.v2.processor_v2.deliver_zip')
    @patch('app.collect.is_v2_nifi_message_submission')
    @patch('app.transformation.create.is_v2_nifi_message_submission')
    def test_spp(self,
                 mock_is_nifi_message: Mock,
                 mock_is_nifi_message_2: Mock,
                 mock_deliver: Mock,
                 mock_zip: Mock,
                 mock_index: Mock,
                 mock_image: Mock,
                 mock_spp: Mock,
                 _mock_receipt: Mock,
                 _mock_comments: Mock,
                 mock_decrypt: Mock,
                 mock_app: Mock):
        tx_id = '0f534ffc-9442-414c-b39f-a756b4adc6cb'
        survey_id = "009"
        period_id = "2510"
        ru_ref = "49900000001A"
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
