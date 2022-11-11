import json
import unittest
from unittest import mock

from app.errors import QuarantinableError
from app.receipt import make_receipt, send_receipt, publish_data, make_srm_receipt
from tests import get_data


class TestReceipt(unittest.TestCase):

    def setUp(self):
        self.test_data = {
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
        expected = json.dumps({"caseId": "123", "partyId": "user_id"})
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

    def test_make_receipt_bad(self):
        data = self.test_data
        del data["case_id"]
        with self.assertRaises(QuarantinableError):
            make_receipt(data)

    @mock.patch('app.receipt.CONFIG')
    def test_publish_data(self, mock_config):
        receipt_topic = "receipt_topic"
        receipt = "my_receipt"
        tx_id = "123"

        mock_config.RECEIPT_TOPIC_PATH = receipt_topic
        publish_data(receipt, tx_id, receipt_topic)

        mock_config.RECEIPT_PUBLISHER.publish.assert_called_with(
            receipt_topic,
            receipt.encode("utf-8"),
            tx_id=tx_id)

    def test_make_adhoc_receipt_valid(self):
        expected = json.dumps({"data": {"qid": "0130000000000300"}})
        self.assertEqual(make_srm_receipt(get_data("survey_adhoc_001")), expected)

    @mock.patch('app.receipt.publish_data')
    def test_send_adhoc_receipt_good(self, mock_publish):
        send_receipt(get_data("survey_adhoc_001"))
