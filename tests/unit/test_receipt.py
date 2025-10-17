import json
import unittest

from app.definitions.submission import SurveySubmission
from app.response import Response
from app.services.receipt import ReceiptService


class MockReceiptPublisher:

    def __init__(self):
        self.receipt: dict[str, str] = {}
        self.receipt_topic: str = ""

    def publish_message(self, topic_path: str, message: str, attributes: dict[str, str]) -> str:
        self.receipt = json.loads(message)
        self.receipt_topic = topic_path
        return ""


class MockReceiptSettings:
    receipt_topic_path: str
    srm_receipt_topic_path: str

    def __init__(self):
        self.receipt_topic_path = "receipt_topic_path"
        self.srm_receipt_topic_path = "srm_receipt_topic_path"


class TestReceipt(unittest.TestCase):

    def setUp(self):

        self.test_submission: SurveySubmission = {
            "tx_id": "1027a13a-c253-4e9d-9e78-d0f0cfdd3988",
            "type": "uk.gov.ons.edc.eq:surveyresponse",
            "case_id": "bb9eaf11-a729-40b5-8d17-d112e018c0d5",
            "origin": "uk.gov.ons.edc.eq",
            "started_at": "2019-04-01T14:00:24.224709",
            "submitted_at": "2019-04-01T14:10:26.933601",
            "version": "v2",
            "collection_exercise_sid": "664dbdf4-02fb-4d68-b0cf-7f7402df00e5",
            "flushed": False,
            "data_version": "0.0.1",
            "launch_language_code": "en",
            "survey_metadata": {
                "survey_id": "017",
                "form_type": "0011",
                "period_id": "201904",
                "ref_p_end_date": "2018-11-29",
                "ref_p_start_date": "2019-04-01",
                "ru_ref": "15162882666F",
                "user_id": "123456",
                "ru_name": "Test Name"
            },
            "data": {
                "15": "No",
                "119": "150",
                "120": "152",
                "144": "200",
                "145": "124",
                "146": "This is a comment"
            }
        }

    def test_send_receipt(self):
        mock_publisher = MockReceiptPublisher()
        mock_settings = MockReceiptSettings()
        rs = ReceiptService(mock_settings, mock_publisher)
        rs.send_receipt(Response(self.test_submission))

        expected_receipt = {
                'caseId': "bb9eaf11-a729-40b5-8d17-d112e018c0d5",
                'partyId': "123456"
            }

        self.assertEqual(expected_receipt, mock_publisher.receipt)
        self.assertEqual(mock_settings.receipt_topic_path, mock_publisher.receipt_topic)

    def test_send_adhoc_receipt(self):
        mock_publisher = MockReceiptPublisher()
        mock_settings = MockReceiptSettings()
        rs = ReceiptService(mock_settings, mock_publisher)
        submission = self.test_submission
        submission["survey_metadata"]["survey_id"] = "740"
        submission["survey_metadata"]["qid"] = "0130000001408548"
        rs.send_receipt(Response(self.test_submission))

        expected_receipt = {
                'data': {
                    'qid': "0130000001408548"
                }
            }

        self.assertEqual(expected_receipt, mock_publisher.receipt)
        self.assertEqual(mock_settings.srm_receipt_topic_path, mock_publisher.receipt_topic)
