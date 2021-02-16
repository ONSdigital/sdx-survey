import json
import unittest

from app.receipt import make_receipt


class TestCollect(unittest.TestCase):

    def test_make_receipt_valid(self):
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
        expected = json.dumps({"case_id": "123", "tx_id": "tx_id", "collection": {"exercise_sid": "exercise_sid"}, "metadata": {"ru_ref": "ru_ref", "user_id": "user_id"}})
        self.assertEqual(make_receipt(test_data), expected)
