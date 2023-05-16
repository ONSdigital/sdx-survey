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
    @patch('app.collect.validate')
    def test_failed_validation_raises_exception(self, validate, decrypt, app):
        app.gcs_read.return_value = b'{"value": "nonsense"}'
        decrypt.return_value = {'value': 'nonsense'}
        validate.return_value = False
        with self.assertRaises(DataError):
            process(self.message)

    @patch('app.collect.sdx_app')
    @patch('app.collect.decrypt_survey')
    @patch('app.collect.validate')
    @patch('app.collect.deliver_feedback')
    @patch('app.collect.send_receipt')
    def test_process_feedback(self, send_receipt, deliver_feedback, validate, decrypt, app):
        tx_id = '0f534ffc-9442-414c-b39f-a756b4adc6cb'
        feedback_response = {
            'tx_id': tx_id,
            'survey_id': '023',
            'type': 'uk.gov.ons.edc.eq:feedback'
        }

        app.gcs_read.return_value = json.dumps(feedback_response).encode()
        decrypt.return_value = feedback_response
        validate.return_value = True
        process(self.message)
        deliver_feedback.assert_called_with(feedback_response, filename=tx_id, version='v1')
        send_receipt.assert_not_called()

    @patch('app.collect.sdx_app')
    @patch('app.collect.decrypt_survey')
    @patch('app.collect.validate')
    @patch('app.collect.store_comments')
    @patch('app.collect.deliver_dap')
    @patch('app.collect.send_receipt')
    def test_process_dap_survey(self, send_receipt, deliver_dap, store_comments, validate, decrypt, app):
        dap_response = {
            'tx_id': '0f534ffc-9442-414c-b39f-a756b4adc6cb',
            'survey_id': '283',
            'type': 'uk.gov.ons.edc.eq:surveyresponse'
        }

        app.gcs_read.return_value = json.dumps(dap_response).encode()
        decrypt.return_value = dap_response
        validate.return_value = True

        process(self.message)

        store_comments.assert_called_with(dap_response)
        deliver_dap.assert_called_with(dap_response, V1)
        send_receipt.assert_called_with(dap_response)

    @patch('app.collect.sdx_app')
    @patch('app.collect.decrypt_survey')
    @patch('app.collect.validate')
    @patch('app.collect.store_comments')
    @patch('app.collect.transform')
    @patch('app.collect.deliver_survey')
    @patch('app.collect.send_receipt')
    def test_process_legacy_survey(self, send_receipt, deliver_survey, transform, store_comments, validate, decrypt, app):
        legacy_response = {
            'tx_id': '0f534ffc-9442-414c-b39f-a756b4adc6cb',
            'survey_id': '202',
            'type': 'uk.gov.ons.edc.eq:surveyresponse'
        }

        app.gcs_read.return_value = json.dumps(legacy_response).encode()
        decrypt.return_value = legacy_response
        validate.return_value = True
        zip_bytes = b"zip bytes"
        transform.return_value = zip_bytes

        process(self.message)

        store_comments.assert_called_with(legacy_response)
        deliver_survey.assert_called_with(legacy_response, zip_bytes, V1)
        send_receipt.assert_called_with(legacy_response)

    @patch('app.collect.sdx_app')
    @patch('app.collect.decrypt_survey')
    @patch('app.collect.validate')
    @patch('app.collect.store_comments')
    @patch('app.collect.transform')
    @patch('app.collect.deliver_hybrid')
    @patch('app.collect.send_receipt')
    def test_process_hybrid_survey(self, send_receipt, deliver_hybrid, transform, store_comments, validate, decrypt, app):
        hybrid_response = {
            'tx_id': '0f534ffc-9442-414c-b39f-a756b4adc6cb',
            'survey_id': '147',
            'type': 'uk.gov.ons.edc.eq:surveyresponse'
        }

        app.gcs_read.return_value = json.dumps(hybrid_response).encode()
        decrypt.return_value = hybrid_response
        validate.return_value = True
        zip_bytes = b"zip bytes"
        transform.return_value = zip_bytes

        process(self.message)

        store_comments.assert_called_with(hybrid_response)
        deliver_hybrid.assert_called_with(hybrid_response, zip_bytes, V1)
        send_receipt.assert_called_with(hybrid_response)
