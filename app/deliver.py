import json
import time

import structlog
import requests
import google.auth.transport.requests
import google.oauth2.id_token

from app import CONFIG
from app.errors import QuarantinableError, RetryableError
from app.submission_type import get_tx_id


# Constants used within the http request
DAP = "dap"
LEGACY = "legacy"
HYBRID = "hybrid"
FEEDBACK = "feedback"
SUBMISSION_FILE = 'submission'
TRANSFORMED_FILE = 'transformed'
UTF8 = "utf-8"
FILE_NAME = "filename"
VERSION = "version"
V1 = "v1"
V2 = "v2"
ADHOC = "adhoc"

logger = structlog.get_logger()


def deliver_dap(submission: dict, version: str = V1):
    """deliver a survey submission intended for DAP"""
    logger.info("Sending DAP submission")
    deliver(submission, DAP, version=version)


def deliver_survey(submission: dict, zip_file: bytes, version: str = V1):
    """deliver a survey submission intended for the legacy systems"""
    logger.info("Sending survey submission")
    files = {TRANSFORMED_FILE: zip_file}
    deliver(submission, LEGACY, files, version=version)


def deliver_hybrid(submission: dict, zip_file: bytes, version: str = V1):
    """deliver a survey submission intended for dap and the legacy systems"""
    logger.info("Sending hybrid submission")
    files = {TRANSFORMED_FILE: zip_file}
    deliver(submission, HYBRID, files, version=version)


def deliver_feedback(submission: dict, filename: str, version: str = V1):
    """deliver a feedback survey submission"""
    logger.info(f"Sending feedback submission")
    deliver(submission, FEEDBACK, {}, filename, version=version)


def deliver(
        submission: dict,
        output_type: str,
        files: dict = {},
        filename: str = None,
        version: str = V1):
    """
    Calls the deliver endpoint specified by the output_type parameter.
    Returns True or raises appropriate error on response.
    """
    if not filename:
        filename = get_tx_id(submission)

    files[SUBMISSION_FILE] = json.dumps(submission).encode(UTF8)

    trying = True
    retries = 0
    max_retries = 3
    http_response = None
    while trying:
        try:
            http_response = post(filename, files, output_type, version)
            trying = False
        except RetryableError:
            retries += 1
            if retries > max_retries:
                trying = False
            else:
                # sleep for 20 seconds
                time.sleep(20)
                logger.info("trying again...")

    if http_response:
        status_code = http_response.status_code
        if status_code == 200:
            return True
        elif 400 <= status_code < 500:
            msg = f"Bad Request response from sdx-deliver: {http_response.reason}"
            logger.error(msg, status_code=status_code)
            raise QuarantinableError(msg)
        else:
            msg = f"Bad Request response from sdx-deliver: {http_response.reason}"
            logger.error(msg, status_code=status_code)
            raise RetryableError(msg)
    else:
        msg = f"No response from sdx-deliver!"
        logger.error(msg)
        raise RetryableError(msg)


def post(filename: str, files: dict, output_type: str, version: str):
    """Constructs the http call to the deliver service endpoint and posts the request"""
    audience = CONFIG.DELIVER_SERVICE_URL
    endpoint = f"{audience}/deliver/{output_type}"
    auth_req = google.auth.transport.requests.Request()
    id_token = google.oauth2.id_token.fetch_id_token(auth_req, audience)
    logger.info(f"Calling {endpoint}")

    try:
        response = requests.post(
            endpoint,
            params={FILE_NAME: filename, VERSION: version},
            files=files,
            headers={"Authorization": f"Bearer {id_token}"}
        )

    except ConnectionError:
        logger.error("Connection error", request_url=endpoint)
        raise RetryableError("Connection error")

    return response
