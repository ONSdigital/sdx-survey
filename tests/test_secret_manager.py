import unittest
from unittest.mock import Mock, patch

from app import get_secret


class TestSecret(unittest.TestCase):

    def setUp(self):
        pass

    @patch('app.secret_manager.secretmanager')
    def test_get_secret(self, mock_secret_manager):
        project_id = "ons-sdx-sandbox"
        secret_id = "my_key"
        secret = "my-secret"
        client_mock = Mock()
        response_mock = Mock()
        response_mock.payload.data.decode = Mock(return_value=secret)

        client_mock.access_secret_version = Mock(return_value=response_mock)
        mock_secret_manager.SecretManagerServiceClient = Mock(return_value=client_mock)

        self.assertEqual(secret, get_secret(project_id, secret_id))


