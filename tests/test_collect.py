import unittest
from unittest.mock import patch

from app.collect import process, is_feedback
from app.errors import QuarantinableError


class TestCollect(unittest.TestCase):

    @patch('app.collect.decrypt_survey')
    @patch('app.collect.validate')
    def test_failed_validation_raises_exception(self, validate, decrypt):
        decrypt.return_value = {'value': 'nonsense'}
        validate.return_value = False
        self.assertRaises(QuarantinableError, process, 'nonsense survey')

    @patch('app.collect.decrypt_survey')
    @patch('app.collect.validate')
    @patch('app.collect.deliver_feedback')
    def test_process_feedback(self, deliver_feedback, validate, decrypt):

        feedback_response = {
            'tx_id': '0f534ffc-9442-414c-b39f-a756b4adc6cb',
            'survey_id': '023',
            'type': 'uk.gov.ons.edc.eq:feedback'
        }

        decrypt.return_value = feedback_response
        validate.return_value = True
        process('encrypted feedback')
        deliver_feedback.assert_called_with(feedback_response)

    @patch('app.collect.decrypt_survey')
    @patch('app.collect.validate')
    @patch('app.collect.deliver_feedback')
    def test_process_feedback(self, deliver_feedback, validate, decrypt):
        feedback_response = {
            'tx_id': '0f534ffc-9442-414c-b39f-a756b4adc6cb',
            'survey_id': '023',
            'type': 'uk.gov.ons.edc.eq:feedback'
        }

        decrypt.return_value = feedback_response
        validate.return_value = True
        process('encrypted feedback')
        deliver_feedback.assert_called_with(feedback_response)

    @patch('app.collect.decrypt_survey')
    @patch('app.collect.validate')
    @patch('app.collect.store_comments')
    @patch('app.collect.deliver_dap')
    @patch('app.collect.send_receipt')
    def test_process_dap_survey(self, send_receipt, deliver_dap, store_comments, validate, decrypt):
        dap_response = {
            'tx_id': '0f534ffc-9442-414c-b39f-a756b4adc6cb',
            'survey_id': '023',
            'type': 'uk.gov.ons.edc.eq:surveyresponse'
        }

        decrypt.return_value = dap_response
        validate.return_value = True

        process('encrypted dap survey')

        store_comments.assert_called_with(dap_response)
        deliver_dap.assert_called_with(dap_response)
        send_receipt.assert_called_with(dap_response)

    @patch('app.collect.decrypt_survey')
    @patch('app.collect.validate')
    @patch('app.collect.store_comments')
    @patch('app.collect.transform')
    @patch('app.collect.deliver_survey')
    @patch('app.collect.send_receipt')
    def test_process_legacy_survey(self, send_receipt, deliver_survey, transform, store_comments, validate, decrypt):
        legacy_response = {
            'tx_id': '0f534ffc-9442-414c-b39f-a756b4adc6cb',
            'survey_id': '009',
            'type': 'uk.gov.ons.edc.eq:surveyresponse'
        }

        decrypt.return_value = legacy_response
        validate.return_value = True
        zip_bytes = b"zip bytes"
        transform.return_value = zip_bytes

        process('encrypted legacy survey')

        store_comments.assert_called_with(legacy_response)
        deliver_survey.assert_called_with(legacy_response, zip_bytes)
        send_receipt.assert_called_with(legacy_response)

    def test_is_feedback(self):
        feedback_response = {
            'tx_id': '0f534ffc-9442-414c-b39f-a756b4adc6cb',
            'survey_id': '023',
            'type': 'uk.gov.ons.edc.eq:feedback'
        }
        feedback = is_feedback(feedback_response)
        self.assertTrue(feedback)

        feedback_response['type'] = 'uk.gov.ons.edc.eq:surveyresponse'
        feedback = is_feedback(feedback_response)
        self.assertFalse(feedback)
