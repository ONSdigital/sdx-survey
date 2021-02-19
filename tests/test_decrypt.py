import unittest
import json
import yaml
from sdc.crypto.key_store import KeyStore
from sdc.crypto.encrypter import encrypt

from app.decrypt import decrypt_survey


def encrypt_survey(submission: dict) -> str:
    with open("./tests/keys.yml") as file:
        secrets_from_file = yaml.safe_load(file)
    key_store = KeyStore(secrets_from_file)
    payload = encrypt(submission, key_store, 'submission')
    return payload


class TestDecrypt(unittest.TestCase):

    def test_decrypt_survey(self):
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
        self.assertEqual(decrypted_message, message_dict)
