import unittest
import json
from unittest.mock import patch

from sdc.crypto.encrypter import encrypt
from app.decrypt import decrypt_survey, load_keys


def encrypt_survey(submission: dict) -> str:
    key1 = open("test_sdx-public-jwt.yaml")
    key2 = open("test_eq-private-signing.yaml")
    key_store = load_keys(key1, key2)
    payload = encrypt(submission, key_store, 'submission')
    key1.close()
    key2.close()
    return payload


class TestDecrypt(unittest.TestCase):

    @patch('app.decrypt.CONFIG')
    def test_decrypt_survey(self, mock_config):

        key_file1 = open("test_sdx-private-jwt.yaml")
        mock_config.DECRYPT_SURVEY_KEY = key_file1

        key_file2 = open("test_eq-public-signing.yaml")
        mock_config.AUTHENTICATE_SURVEY_KEY = key_file2

        message_dict = json.loads('''{
            "collection": {
                "exercise_sid": "XxsteeWv",
                "instrument_id": "0167",
                "period": "2019"
            },
            "data": {
                "46": "123",
                "47": "456",
                "50": "789",
                "51": "111",
                "52": "222",
                "53": "333",
                "54": "444",
                "146": "different comment.",
                "d12": "Yes",
                "d40": "Yes"
            },
            "flushed": false,
            "metadata": {
                "ref_period_end_date": "2016-05-31",
                "ref_period_start_date": "2016-05-01",
                "ru_ref": "49900108249D",
                "user_id": "UNKNOWN"
            },
            "origin": "uk.gov.ons.edc.eq",
            "started_at": "2017-07-05T10:54:11.548611+00:00",
            "submitted_at": "2017-07-05T14:49:33.448608+00:00",
            "type": "uk.gov.ons.edc.eq:surveyresponse",
            "version": "0.0.1",
            "survey_id": "009",
            "tx_id": "c37a3efa-593c-4bab-b49c-bee0613c4fb2",
            "case_id": "4c0bc9ec-06d4-4f66-88b6-2e42b79f17b3"
        }''')
        encrypted_message = encrypt_survey(message_dict)
        decrypted_message = decrypt_survey(encrypted_message)
        key_file1.close()
        key_file2.close()
        self.assertEqual(decrypted_message, message_dict)
