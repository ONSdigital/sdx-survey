import unittest
from unittest import mock
from unittest.mock import patch

from google.cloud.pubsub_v1.subscriber.message import Message

from app.errors import QuarantinableError
from app.subscriber import callback


class TestCollect(unittest.TestCase):

    @patch.object(Message, 'ack')
    @mock.patch('app.subscriber.process', side_effect=QuarantinableError())
    @mock.patch('app.subscriber.quarantine_message')
    def test_process_no_data(self, mock_quarantine, mock_process, mock_message):
        mock_message.data = None
        callback(mock_message)
        mock_quarantine.assert_called()

    @patch.object(Message, 'ack')
    @mock.patch('app.subscriber.process', side_effect=QuarantinableError())
    @mock.patch('app.subscriber.quarantine_submission')
    def test_process_no_data(self, quarantine_submission, mock_process, mock_message):
        mock_message.data = 'Survey data goes here'
        callback(mock_message)
        quarantine_submission.assert_called()
