import unittest
from typing import Any

import yaml
from sdc.crypto.encrypter import encrypt
from sdc.crypto.key_store import KeyStore
from sdx_base.settings.service import SECRET

from app.definitions.submission import SurveySubmission
from app.services.decrypter import DecryptionService

KEY_DIR = "tests/data/keys"


def encrypt_survey(data: Any) -> str:
    key1 = open(f"{KEY_DIR}/test_sdx-public-jwt.yaml")
    key2 = open(f"{KEY_DIR}/test_eq-private-signing.yaml")

    key_store = load_keys(key1, key2)
    payload = encrypt(data, key_store, "submission")
    key1.close()
    key2.close()
    return payload


def load_keys(*keys) -> KeyStore:
    key_dict = {}
    for k in keys:
        key = yaml.safe_load(k)
        key_dict[key["keyid"]] = key
    return KeyStore({"keys": key_dict})


submission: SurveySubmission = {
    "tx_id": "1027a13a-c253-4e9d-9e78-d0f0cfdd3988",
    "type": "uk.gov.ons.edc.eq:surveyresponse",
    "case_id": "bb9eaf11-a729-40b5-8d17-d112e018c0d5",
    "origin": "uk.gov.ons.edc.eq",
    "started_at": "2019-04-01T14:00:24.224709",
    "submitted_at": "2019-04-01T14:10:26.933601",
    "version": "v2",
    "collection_exercise_sid": "664dbdf4-02fb-4d68-b0cf-7f7402df00e5",
    "flushed": False,
    "data_version": "0.0.1",
    "launch_language_code": "en",
    "survey_metadata": {
        "survey_id": "017",
        "form_type": "0011",
        "period_id": "201904",
        "ref_p_end_date": "2018-11-29",
        "ref_p_start_date": "2019-04-01",
        "ru_ref": "15162882666F",
        "user_id": "UNKNOWN",
        "ru_name": "Test Name",
    },
    "data": {"15": "No", "119": "150", "120": "152", "144": "200", "145": "124", "146": "This is a comment"},
}


class MockDecryptionKeys:
    sdx_private_jwt: SECRET
    eq_public_signing: SECRET
    eq_public_jws: SECRET

    def __init__(self):
        with open(f"{KEY_DIR}/test_sdx-private-jwt.yaml") as k:
            self.sdx_private_jwt: SECRET = k.read()

        with open(f"{KEY_DIR}/test_eq-public-signing.yaml") as k:
            self.eq_public_signing: SECRET = k.read()

        self.eq_public_jws: SECRET = self.eq_public_signing


class TestDecrypt(unittest.TestCase):
    def test_decrypt_survey(self):
        encrypted_message = encrypt_survey(submission)
        service = DecryptionService(MockDecryptionKeys())
        decrypted_message = service.decrypt_survey(encrypted_message)

        self.assertEqual(decrypted_message, submission)
