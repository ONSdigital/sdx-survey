import json
import unittest
from unittest.mock import patch

from sdx_gcp import Message
from sdx_gcp.errors import DataError

from app.collect import process
from app.deliver import V1


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
    @patch('app.processor.deliver_feedback')
    @patch('app.processor.send_receipt')
    def test_process_feedback(self, send_receipt, deliver_feedback, decrypt, app):
        tx_id = '0f534ffc-9442-414c-b39f-a756b4adc6cb'
        feedback_response = {
            'tx_id': tx_id,
            'survey_id': '023',
            'type': 'uk.gov.ons.edc.eq:feedback'
        }

        app.gcs_read.return_value = json.dumps(feedback_response).encode()
        decrypt.return_value = feedback_response
        process(self.message, tx_id)
        deliver_feedback.assert_called_with(feedback_response, tx_id=tx_id, filename=tx_id, version='v1')
        send_receipt.assert_not_called()

    @patch('app.collect.sdx_app')
    @patch('app.collect.decrypt_survey')
    @patch('app.processor.store_comments')
    @patch('app.processor.deliver_dap')
    @patch('app.processor.send_receipt')
    def test_process_dap_survey(self, send_receipt, deliver_dap, store_comments, decrypt, app):
        dap_response = {
            'tx_id': '0f534ffc-9442-414c-b39f-a756b4adc6cb',
            'survey_id': '283',
            'type': 'uk.gov.ons.edc.eq:surveyresponse'
        }

        app.gcs_read.return_value = json.dumps(dap_response).encode()
        decrypt.return_value = dap_response

        process(self.message, "0f534ffc-9442-414c-b39f-a756b4adc6cb")

        store_comments.assert_called_with(dap_response)
        deliver_dap.assert_called_with(dap_response, tx_id='0f534ffc-9442-414c-b39f-a756b4adc6cb', version=V1)
        send_receipt.assert_called_with(dap_response)

    @patch('app.collect.sdx_app')
    @patch('app.collect.decrypt_survey')
    @patch('app.collect.store_comments')
    @patch('app.collect.transform')
    @patch('app.collect.deliver_survey')
    @patch('app.collect.send_receipt')
    def test_process_legacy_survey(self, send_receipt, deliver_survey, transform, store_comments, decrypt, app):
        tx_id = '0f534ffc-9442-414c-b39f-a756b4adc6cb'
        legacy_response = {
            'tx_id': tx_id,
            'survey_id': '202',
            'type': 'uk.gov.ons.edc.eq:surveyresponse'
        }

        app.gcs_read.return_value = json.dumps(legacy_response).encode()
        decrypt.return_value = legacy_response
        zip_bytes = b"zip bytes"
        transform.return_value = zip_bytes

        process(self.message, tx_id)

        store_comments.assert_called_with(legacy_response)
        deliver_survey.assert_called_with(legacy_response,
                                          zip_bytes,
                                          tx_id=tx_id,
                                          version=V1)
        send_receipt.assert_called_with(legacy_response)

    @patch('app.collect.sdx_app')
    @patch('app.collect.decrypt_survey')
    @patch('app.processor.store_comments')
    @patch('app.processor.transform')
    @patch('app.processor.deliver_hybrid')
    @patch('app.processor.send_receipt')
    def test_process_hybrid_survey(self, send_receipt, deliver_hybrid, transform, store_comments, decrypt, app):
        hybrid_response = {
            'tx_id': '0f534ffc-9442-414c-b39f-a756b4adc6cb',
            'survey_id': '147',
            'type': 'uk.gov.ons.edc.eq:surveyresponse'
        }

        app.gcs_read.return_value = json.dumps(hybrid_response).encode()
        decrypt.return_value = hybrid_response
        zip_bytes = b"zip bytes"
        transform.return_value = zip_bytes

        process(self.message, "0f534ffc-9442-414c-b39f-a756b4adc6cb")

        store_comments.assert_called_with(hybrid_response)
        deliver_hybrid.assert_called_with(hybrid_response,
                                          zip_bytes,
                                          tx_id='0f534ffc-9442-414c-b39f-a756b4adc6cb',
                                          version=V1)
        send_receipt.assert_called_with(hybrid_response)
