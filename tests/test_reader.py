import unittest
from unittest.mock import patch

from app import CONFIG
from app.reader import read


class TestReader(unittest.TestCase):

    @patch('app.reader.CONFIG.BUCKET')
    def test_reader(self, mock_storage):
        filename = 'test_file'
        storage_client = mock_storage.Client
        bucket = storage_client(CONFIG.PROJECT_ID).bucket
        blob = bucket(CONFIG.BUCKET_NAME).blob
        data_bytes = blob.download_as_bytes
        read(filename)
        storage_client.assert_called_with(CONFIG.PROJECT_ID)
        bucket.assert_called_with(CONFIG.BUCKET_NAME)
        data_bytes.return_value.decode.return_value = b"file_content"
