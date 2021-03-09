import binascii
import structlog
import yaml

from cryptography import exceptions
from sdc.crypto.exceptions import InvalidTokenException
from sdc.crypto.key_store import KeyStore
from sdc.crypto.decrypter import decrypt as sdc_decrypt
from app import CONFIG
from app.errors import QuarantinableError

KEY_PURPOSE_SUBMISSION = 'submission'

logger = structlog.get_logger()


def decrypt_survey(payload: str) -> dict:
    logger.info("Decrypting survey")

    try:
        key_store = load_keys(CONFIG.DECRYPT_SURVEY_KEY, CONFIG.AUTHENTICATE_SURVEY_KEY)
        decrypted_dict = sdc_decrypt(payload, key_store, KEY_PURPOSE_SUBMISSION)
        logger.info("Successfully decrypted")
        return decrypted_dict

    except (
            exceptions.UnsupportedAlgorithm,
            exceptions.InvalidKey,
            exceptions.AlreadyFinalized,
            exceptions.InvalidSignature,
            exceptions.NotYetFinalized,
            exceptions.AlreadyUpdated):

        raise QuarantinableError("Decryption Failure")
    except binascii.Error as e:
        logger.exception(e)
        raise QuarantinableError("Request payload was not base64 encoded")
    except InvalidTokenException as e:
        logger.exception(repr(e))
        raise QuarantinableError(e)


def load_keys(*keys) -> KeyStore:
    key_dict = {}
    for k in keys:
        key = yaml.safe_load(k)
        key_dict[key['keyid']] = key
    return KeyStore({"keys": key_dict})
