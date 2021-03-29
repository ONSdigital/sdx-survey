import unittest
from unittest import mock
from unittest.mock import patch

from google.cloud.pubsub_v1.subscriber.message import Message

from app.errors import QuarantinableError, RetryableError
from app.subscriber import callback


class TestCollect(unittest.TestCase):

    @patch.object(Message, 'ack')
    @mock.patch('app.subscriber.process')
    @mock.patch('app.subscriber.quarantine_message')
    def test_quarantine_no_data(self, quarantine_message, mock_process, mock_message):
        mock_message.data = None
        mock_process.side_effect = QuarantinableError()
        callback(mock_message)
        quarantine_message.assert_called()

    @patch.object(Message, 'ack')
    @mock.patch('app.subscriber.process')
    @mock.patch('app.subscriber.quarantine_submission')
    def test_quarantine_with_data(self, quarantine_submission, mock_process, mock_message):
        mock_message.data = b'Test Data'
        mock_process.side_effect = QuarantinableError()
        callback(mock_message)
        quarantine_submission.assert_called()

    @patch.object(Message, 'ack')
    @mock.patch('app.subscriber.process')
    @mock.patch('app.subscriber.quarantine_submission')
    @mock.patch('app.subscriber.quarantine_message')
    def test_retryable_error(self, quarantine_message, quarantine_submission, mock_process, mock_message):
        mock_message.attributes = {'tx_id': 'tx_id'}
        mock_process.side_effect = RetryableError()
        callback(mock_message.data)
        quarantine_submission.assert_not_called()
        quarantine_message.assert_not_called()
