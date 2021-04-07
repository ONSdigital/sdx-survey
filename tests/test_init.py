import unittest
from unittest.mock import patch, Mock

from app import cloud_config, project_id


class TestInit(unittest.TestCase):

    @patch('app.get_secret')
    @patch('app.pubsub_v1')
    @patch('app.datastore')
    def test_cloud_config(self, mock_datastore, mock_pubsub, mock_get_secret):
        mock_pubsub.SubscriberClient.return_value = Mock()
        ds_client = Mock()
        mock_datastore.Client = ds_client
        cloud_config()
        ds_client.assert_called_with(project=project_id)
