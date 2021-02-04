import binascii
import logging
import yaml
from cryptography import exceptions
from sdc.crypto.exceptions import InvalidTokenException
from sdc.crypto.key_store import KeyStore
from sdc.crypto.decrypter import decrypt as sdc_decrypt
from structlog import wrap_logger
from app import DECRYPT_SURVEY_KEY

from app.errors import ClientError

KEY_PURPOSE_SUBMISSION = 'submission'

logger = wrap_logger(logging.getLogger(__name__))


def decrypt_survey(payload: str) -> dict:
    logger.info("decrypting survey")

    try:
        decrypt_key_yaml = yaml.safe_load(DECRYPT_SURVEY_KEY)
        key_store = KeyStore(decrypt_key_yaml)
        decrypted_json = sdc_decrypt(payload, key_store, KEY_PURPOSE_SUBMISSION)
        logger.info("survey successfully decrypted")
        return decrypted_json

    except (
            exceptions.UnsupportedAlgorithm,
            exceptions.InvalidKey,
            exceptions.AlreadyFinalized,
            exceptions.InvalidSignature,
            exceptions.NotYetFinalized,
            exceptions.AlreadyUpdated):

        raise ClientError("Decryption Failure")
    except binascii.Error as e:
        logger.exception(e)
        raise ClientError("Request payload was not base64 encoded")
    except InvalidTokenException as e:
        logger.exception(repr(e))
        raise ClientError(e)
