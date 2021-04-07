import unittest
from unittest.mock import patch

from app.quarantine import quarantine_submission, quarantine_message


class TestQuarantine(unittest.TestCase):

    @patch('app.quarantine.CONFIG')
    def test_quarantine_submission(self, mock_config):
        mock_config.QUARANTINE_TOPIC_PATH = "quarantine_path"
        data_str = "my data"
        tx_id = "123"
        error = "bad error"

        quarantine_submission(data_str, tx_id, error)

        mock_config.QUARANTINE_PUBLISHER.publish.assert_called_with(
            mock_config.QUARANTINE_TOPIC_PATH,
            data_str.encode("utf-8"),
            tx_id=tx_id,
            error=error)

    @patch('app.quarantine.CONFIG')
    def test_quarantine_message(self, mock_config):
        mock_config.QUARANTINE_TOPIC_PATH = "quarantine_path"
        message = b"my message"
        tx_id = "123"
        error = "bad error"

        quarantine_message(message, tx_id, error)

        mock_config.QUARANTINE_PUBLISHER.publish.assert_called_with(
            mock_config.QUARANTINE_TOPIC_PATH,
            message,
            tx_id=tx_id,
            error=error)
