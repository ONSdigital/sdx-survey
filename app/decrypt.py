import logging

import yaml
from sdc.crypto.key_store import KeyStore
from sdc.crypto.decrypter import decrypt as sdc_decrypt
from structlog import wrap_logger

KEY_PURPOSE_SUBMISSION = 'submission'

logger = wrap_logger(logging.getLogger(__name__))


def decrypt_survey(payload: str) -> dict:
    logger.info("decrypting survey")
    with open("./keys2.yaml") as file2:
        secrets_from_file2 = yaml.safe_load(file2)
    key_store2 = KeyStore(secrets_from_file2)
    decrypted_json = sdc_decrypt(payload, key_store2, KEY_PURPOSE_SUBMISSION)
    logger.info("survey successfully decrypted")
    return decrypted_json
