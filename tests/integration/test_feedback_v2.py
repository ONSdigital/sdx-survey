import json
import unittest
from unittest.mock import patch, Mock

from sdx_gcp import Message

from app.collect import process
from app.definitions.submission import SurveySubmission
from app.definitions.v2_context_type import V2ContextType
from app.definitions.v2_survey_type import V2SurveyType
from app.v2.context import Context
from tests import get_json


class TestFeedback(unittest.TestCase):

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
    @patch('app.transformation.transformers.create_zip')
    @patch('app.v2.processor_v2.deliver_zip')
    @patch('app.collect.is_v2_nifi_message_submission')
    @patch('app.transformation.create.is_v2_nifi_message_submission')
    def test_feedback(self,
                      mock_is_nifi_message: Mock,
                      mock_is_nifi_message_2: Mock,
                      mock_deliver: Mock,
                      mock_zip: Mock,
                      _mock_receipt: Mock,
                      _mock_comments: Mock,
                      mock_decrypt: Mock,
                      mock_app: Mock):
        tx_id = '0f534ffc-9442-414c-b39f-a756b4adc6cb'
        survey_id = "009"
        period_id = "2504"
        ru_ref = "49900000001A"
        zip_bytes = b'the zip bytes'

        submission: SurveySubmission = get_json("feedback_v2_001")
        submission["tx_id"] = tx_id
        submission["survey_metadata"]["survey_id"] = survey_id
        submission["survey_metadata"]["period_id"] = period_id
        submission["survey_metadata"]["ru_ref"] = ru_ref

        mock_is_nifi_message.return_value = True
        mock_is_nifi_message_2.return_value = True
        mock_app.gcs_read.return_value = json.dumps(submission).encode()
        mock_decrypt.return_value = submission
        mock_zip.return_value = zip_bytes

        process(self.message, tx_id)

        expected_files: dict[str, bytes] = {
            '0f534ffc-9442-414c-b39f-a756b4adc6cb-fb-16-37-56_21-05-2016': json.dumps(submission).encode()
        }

        mock_zip.assert_called_with(expected_files)

        expected_zip: bytes = zip_bytes
        expected_context: Context = {
            "tx_id": tx_id,
            "survey_id": survey_id,
            "ru_ref": ru_ref,
            "survey_type": V2SurveyType.FEEDBACK,
            "period_id": period_id,
            "context_type": V2ContextType.BUSINESS_SURVEY
        }

        mock_deliver.assert_called_with(tx_id, expected_zip, expected_context)
