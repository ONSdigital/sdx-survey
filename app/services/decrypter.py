import binascii
from typing import Final, Protocol

import yaml

from cryptography import exceptions
from sdc.crypto.exceptions import InvalidTokenException
from sdc.crypto.key_store import KeyStore
from sdc.crypto.decrypter import decrypt as sdc_decrypt
from sdx_base.errors.errors import DataError
from sdx_base.errors.retryable import RetryableError
from sdx_base.settings.service import SECRET
from sdx_base.utilities.singleton import AbstractSingleton

from app import get_logger
from app.definitions.decrypter import DecryptionBase
from app.definitions.submission import SurveySubmission

logger = get_logger()

KEY_PURPOSE_SUBMISSION: Final[str] = 'submission'


class DecryptionKeys(Protocol):
    sdx_private_jwt: SECRET
    eq_public_signing: SECRET
    eq_public_jws: SECRET


class DecryptionService(DecryptionBase, metaclass=AbstractSingleton):

    def __init__(self, secret_keys: DecryptionKeys):
        keys: dict[str, str] = {}
        for k in [secret_keys.sdx_private_jwt, secret_keys.eq_public_signing, secret_keys.eq_public_jws]:
            key = yaml.safe_load(k)
            keys[key['keyid']] = key
        self.key_store = KeyStore({"keys": keys})

    def decrypt_survey(self, payload: str) -> SurveySubmission:
        """
        Decrypts an encrypted json survey submission

        The payload needs to be a JWE encrypted using SDX's public key.
        The JWE ciphertext should represent a JWS signed by EQ using
        their private key and with the survey json as the claims set.

        :param payload:  JWE as a string
        :return:  The survey submission json as a dictionary
        """

        logger.info("Decrypting survey")

        try:
            decrypted_dict = sdc_decrypt(payload, self.key_store, KEY_PURPOSE_SUBMISSION)
            logger.info("Successfully decrypted")
            return decrypted_dict

        except (
                exceptions.UnsupportedAlgorithm,
                exceptions.InvalidKey,
                exceptions.AlreadyFinalized,
                exceptions.InvalidSignature,
                exceptions.NotYetFinalized,
                exceptions.AlreadyUpdated) as e:

            logger.exception(f"Decryption Failure: {e}")
            raise DataError(e)
        except binascii.Error as e:
            logger.exception(f"Request payload was not base64 encoded: {e}")
            raise DataError(e)
        except InvalidTokenException as e:
            logger.exception(repr(e))
            raise DataError(e)
        except Exception as e:
            logger.exception(f"Unexpected exception occurred during decryption: {str(e)}")
            raise RetryableError(e)
