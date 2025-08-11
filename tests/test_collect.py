import json
import unittest
from unittest.mock import patch, Mock

from sdx_gcp import Message
from sdx_gcp.errors import DataError

from app.collect import process
from app.deliver import V2
from app.response import Response


class TestCollect(unittest.TestCase):

    def setUp(self) -> None:
        self.message: Message = {
            "attributes": {"objectId": "0f534ffc-9442-414c-b39f-a756b4adc6cb"},
            "data": "",
            "message_id": "",
            "publish_time": ""
        }

    @patch('app.collect.sdx_app')
    @patch('app.collect.decrypt_survey')
    def test_failed_validation_raises_exception(self, decrypt, app):
        app.gcs_read.return_value = b'{"value": "nonsense"}'
        decrypt.return_value = {'value': 'nonsense'}
        with self.assertRaises(DataError):
            process(self.message, "123")

    @patch('app.collect.sdx_app')
    @patch('app.collect.decrypt_survey')
    @patch('app.collect.is_v2_nifi_message_submission')
    @patch('app.processor.deliver_feedback')
    @patch('app.processor.send_receipt')
    def test_process_feedback(self, send_receipt, deliver_feedback, v2_nifi_message, decrypt, app):
        tx_id = '0f534ffc-9442-414c-b39f-a756b4adc6cb'
        feedback_response = {
            'tx_id': tx_id,
            'survey_id': '023',
            'type': 'uk.gov.ons.edc.eq:feedback'
        }

        app.gcs_read.return_value = json.dumps(feedback_response).encode()
        decrypt.return_value = feedback_response
        v2_nifi_message.return_value = False
        process(self.message, tx_id)
        deliver_feedback.assert_called_with(Response(feedback_response, tx_id), version=V2)
        send_receipt.assert_not_called()

    @patch('app.collect.sdx_app')
    @patch('app.collect.decrypt_survey')
    @patch('app.collect.is_v2_nifi_message_submission')
    @patch('app.processor.store_comments')
    @patch('app.processor.deliver_dap')
    @patch('app.processor.send_receipt')
    def test_process_dap_survey(self, send_receipt, deliver_dap, store_comments, v2_nifi_message, decrypt, app):

        tx_id = "0f534ffc-9442-414c-b39f-a756b4adc6cb"

        dap_response = {
            'tx_id': tx_id,
            'survey_id': '283',
            'type': 'uk.gov.ons.edc.eq:surveyresponse'
        }

        dap_response_object = Response(dap_response, tx_id)

        v2_nifi_message.return_value = False

        app.gcs_read.return_value = json.dumps(dap_response).encode()
        decrypt.return_value = dap_response

        process(self.message, tx_id)

        store_comments.assert_called_with(dap_response_object)
        deliver_dap.assert_called_with(dap_response_object, version=V2)
        send_receipt.assert_called_with(dap_response_object)

    @patch('app.collect.sdx_app')
    @patch('app.collect.decrypt_survey')
    @patch('app.collect.SurveyProcessorV2')
    def test_process_legacy_survey(self, processor_mock: Mock, decrypt: Mock, app: Mock):
        tx_id = '0f534ffc-9442-414c-b39f-a756b4adc6cb'
        legacy_response = {
            'tx_id': tx_id,
            'survey_id': '202',
            'type': 'uk.gov.ons.edc.eq:surveyresponse'
        }

        app.gcs_read.return_value = json.dumps(legacy_response).encode()
        decrypt.return_value = legacy_response

        process(self.message, tx_id)

        processor_mock.assert_called_once_with(Response(legacy_response, tx_id))
        processor_mock.return_value.run.assert_called_once()

    @patch('app.collect.sdx_app')
    @patch('app.collect.decrypt_survey')
    @patch('app.processor.store_comments')
    @patch('app.processor.transform')
    @patch('app.processor.deliver_hybrid')
    @patch('app.processor.send_receipt')
    def test_process_hybrid_survey(self, send_receipt, deliver_hybrid, transform, store_comments, decrypt, app):

        tx_id = '0f534ffc-9442-414c-b39f-a756b4adc6cb'
        hybrid_response = {
            'tx_id': tx_id,
            'survey_id': '147',
            'type': 'uk.gov.ons.edc.eq:surveyresponse'
        }

        app.gcs_read.return_value = json.dumps(hybrid_response).encode()
        decrypt.return_value = hybrid_response
        zip_bytes = b"zip bytes"
        transform.return_value = zip_bytes

        process(self.message, tx_id)

        response_object = Response(hybrid_response, tx_id)

        store_comments.assert_called_with(response_object)
        deliver_hybrid.assert_called_with(response_object,
                                          zip_bytes,
                                          version=V2)
        send_receipt.assert_called_with(response_object)
