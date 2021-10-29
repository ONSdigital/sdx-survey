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
        version_mock = Mock()
        version_mock.state.name = "ENABLED"

        response_mock.payload.data.decode = Mock(return_value=secret)
        client_mock.list_secret_versions = Mock(return_value=[version_mock])
        client_mock.access_secret_version = Mock(return_value=response_mock)
        mock_secret_manager.SecretManagerServiceClient = Mock(return_value=client_mock)

        self.assertEqual([secret], get_secret(project_id, secret_id))

    @patch('app.secret_manager.secretmanager')
    def test_no_enabled_versions(self, mock_secret_manager):
        project_id = "ons-sdx-sandbox"
        secret_id = "my_key"
        secret = "my-secret"
        client_mock = Mock()
        response_mock = Mock()
        version_mock = Mock()
        version_mock.state.name = "DISABLED"

        response_mock.payload.data.decode = Mock(return_value=secret)
        client_mock.list_secret_versions = Mock(return_value=[version_mock])
        client_mock.access_secret_version = Mock(return_value=response_mock)
        mock_secret_manager.SecretManagerServiceClient = Mock(return_value=client_mock)

        self.assertEqual([], get_secret(project_id, secret_id))
