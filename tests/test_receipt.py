import json
import unittest
from unittest import mock

from app.receipt import make_receipt, send_receipt


class TestCollect(unittest.TestCase):
    test_data = {
        "case_id": "123",
        "survey_id": "survey_id",
        "tx_id": "tx_id",
        "collection": {
            "exercise_sid": "exercise_sid"
        },
        "metadata": {
            "ru_ref": "ru_ref",
            "user_id": "user_id"
        }
    }

    def test_make_receipt_valid(self):
        expected = json.dumps({"case_id": "123", "tx_id": "tx_id", "collection": {"exercise_sid": "exercise_sid"},
                               "metadata": {"ru_ref": "ru_ref", "user_id": "user_id"}})
        self.assertEqual(make_receipt(self.test_data), expected)

    @mock.patch('app.receipt.publish_data')
    @mock.patch('app.receipt.make_receipt')
    def test_send_receipt_no_case_id(self, mock_publish, mock_make):
        self.test_data.pop('tx_id')
        mock_make(self.test_data)
        self.assertRaises(KeyError)

    @mock.patch('app.receipt.publish_data')
    def test_send_receipt_good(self, mock_publish):
        send_receipt(self.test_data)

