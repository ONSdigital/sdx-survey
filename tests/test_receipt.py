import unittest

from app.receipt import make_receipt


class TestCollect(unittest.TestCase):

    def test_make_receipt_valid(self):
        test_data = {
            "case_id": "case_id",
            "survey_id": "123",
            "tx_id": "123abc456def",
            "collection": {
                "exercise_sid": "123"
            },
            "metadata": {
                "ru_ref": "ru_ref",
                "user_id": "user_id"
            }
        }
        self.assertEqual(make_receipt, "")