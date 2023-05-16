import binascii

import yaml

from cryptography import exceptions
from sdc.crypto.exceptions import InvalidTokenException
from sdc.crypto.key_store import KeyStore
from sdc.crypto.decrypter import decrypt as sdc_decrypt
from sdx_gcp.app import get_logger
from sdx_gcp.errors import RetryableError, DataError

logger = get_logger()


class Decrypter:

    KEY_PURPOSE_SUBMISSION = 'submission'
    keys = {}
    key_store = KeyStore({"keys": keys})

    def add_key(self, k):
        key = yaml.safe_load(k)
        self.keys[key['keyid']] = key
        self.key_store = KeyStore({"keys": self.keys})

    def decrypt_survey(self, payload: str) -> dict:
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
            decrypted_dict = sdc_decrypt(payload, self.key_store, self.KEY_PURPOSE_SUBMISSION)
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


decrypter = Decrypter()


def decrypt_survey(payload: str) -> dict:
    return decrypter.decrypt_survey(payload)


def add_key(key) -> None:
    decrypter.add_key(key)


def add_keys(keys: list) -> None:
    for key in keys:
        add_key(key)
