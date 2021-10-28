import unittest
from unittest.mock import patch

from app.quarantine import quarantine_submission


class TestQuarantine(unittest.TestCase):

    @patch('app.quarantine.CONFIG')
    def test_quarantine_submission(self, mock_config):
        mock_config.QUARANTINE_TOPIC_PATH = "quarantine_path"
        tx_id = "123"
        error = "bad error"

        quarantine_submission(tx_id, error)

        mock_config.QUARANTINE_PUBLISHER.publish.assert_called_with(
            mock_config.QUARANTINE_TOPIC_PATH,
            error.encode(),
            tx_id=tx_id,
            error=error)
