import unittest
from concurrent import futures
from unittest import mock
from unittest.mock import patch, Mock

from google.cloud.pubsub_v1.subscriber.message import Message

from app.errors import QuarantinableError, RetryableError
from app.subscriber import callback, start


class TestSubsrciber(unittest.TestCase):

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

    @mock.patch('app.subscriber.CONFIG')
    def test_start_timeout(self, mock_config):
        streaming_pull_future = Mock()
        streaming_pull_future.result = Mock(side_effect=futures.TimeoutError)
        mock_config.SURVEY_SUBSCRIBER.subscribe = Mock(return_value=streaming_pull_future)

        start()

        streaming_pull_future.cancel.assert_called()

    @mock.patch('app.subscriber.process')
    def test_callback(self, mock_process):
        tx_id = "123"
        mock_message = Mock()
        mock_message.attributes.get.return_value = tx_id
        mock_message.data.decode.return_value = 'my message'

        callback(mock_message)

        mock_message.ack.assert_called()
