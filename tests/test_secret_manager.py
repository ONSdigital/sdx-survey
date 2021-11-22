import unittest
from unittest.mock import Mock, patch

from google.api_core.exceptions import NotFound

from app import get_secret_list


class TestSecret(unittest.TestCase):

    def setUp(self):
        pass

    @patch('app.secret_manager.secretmanager')
    def test_get_secret_list(self, mock_secret_manager):
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

        self.assertEqual([secret], get_secret_list(project_id, secret_id))

    @patch('app.secret_manager.secretmanager')
    def test_get_secret_list_2_enabled(self, mock_secret_manager):
        project_id = "ons-sdx-sandbox"
        secret_id = "test_key"
        secret_v1 = "secret-v1"
        secret_v2 = "secret-v2"
        secret_v3 = "secret-v3"
        client_mock = Mock()

        v1 = Mock()
        v2 = Mock()
        v3 = Mock()
        v1.name = "v1"
        v2.name = "v2"
        v3.name = "v3"
        v1.state.name = "DISABLED"
        v2.state.name = "ENABLED"
        v3.state.name = "ENABLED"

        client_mock.list_secret_versions = Mock(return_value=[v1, v2, v3])

        encoded_v1 = Mock()
        encoded_v2 = Mock()
        encoded_v3 = Mock()
        encoded_v1.payload.data.decode = Mock(return_value=secret_v1)
        encoded_v2.payload.data.decode = Mock(return_value=secret_v2)
        encoded_v3.payload.data.decode = Mock(return_value=secret_v3)

        def mock_get_secret(request: dict):
            if request["name"] == "v1":
                return encoded_v1
            elif request["name"] == "v2":
                return encoded_v2
            elif request["name"] == "v3":
                return encoded_v3

        client_mock.access_secret_version = Mock(side_effect=mock_get_secret)

        mock_secret_manager.SecretManagerServiceClient = Mock(return_value=client_mock)

        self.assertEqual([secret_v2, secret_v3], get_secret_list(project_id, secret_id))

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

        self.assertEqual([], get_secret_list(project_id, secret_id))

    @patch('app.secret_manager.secretmanager')
    @patch('app.secret_manager.logger')
    def test_secret_not_found(self, mock_logger, mock_secret_manager):
        project_id = "ons-sdx-sandbox"
        secret_id = "my_key"
        client_mock = Mock()
        exception_mock = Mock()
        mock_logger.exception = exception_mock

        client_mock.list_secret_versions = Mock(side_effect=NotFound("Missing Secret"))
        mock_secret_manager.SecretManagerServiceClient = Mock(return_value=client_mock)

        get_secret_list(project_id, secret_id)
        exception_mock.assert_called()
