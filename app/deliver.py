import json

import requests
import structlog

from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.exceptions import MaxRetryError
from requests.exceptions import ConnectionError

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

session = requests.Session()
retries = Retry(total=5, backoff_factor=0.1)
session.mount('http://', HTTPAdapter(max_retries=retries))


def deliver_dap(submission: dict, version: str = V1):
    """deliver a survey submission intended for DAP"""
    logger.info("Sending DAP submission")
    deliver(submission, DAP)


def deliver_survey(submission: dict, zip_file: bytes, version: str = V1):
    """deliver a survey submission intended for the legacy systems"""
    logger.info("Sending survey submission")
    files = {TRANSFORMED_FILE: zip_file}
    deliver(submission, LEGACY, files)


def deliver_hybrid(submission: dict, zip_file: bytes, version: str = V1):
    """deliver a survey submission intended for dap and the legacy systems"""
    logger.info("Sending hybrid submission")
    files = {TRANSFORMED_FILE: zip_file}
    deliver(submission, HYBRID, files)


def deliver_feedback(submission: dict, filename: str, version: str = V1):
    """deliver a feedback survey submission"""
    logger.info(f"Sending feedback submission")
    deliver(submission, FEEDBACK, {}, filename)


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
    response = post(filename, files, output_type, version)
    status_code = response.status_code

    if status_code == 200:
        return True
    elif 400 <= status_code < 500:
        msg = "Bad Request response from sdx-deliver"
        logger.error(msg, status_code=status_code)
        raise QuarantinableError(msg)
    else:
        msg = "Bad response from sdx-deliver"
        logger.error(msg, status_code=status_code)
        raise RetryableError(msg)


def post(filename: str, files: dict, output_type: str, version: str):
    """Constructs the http call to the deliver service endpoint and posts the request"""

    url = f"http://{CONFIG.DELIVER_SERVICE_URL}/deliver/{output_type}"
    logger.info(f"Calling {url}")
    try:
        response = session.post(url, params={FILE_NAME: filename, VERSION: version}, files=files)
    except MaxRetryError:
        logger.error("Max retries exceeded", request_url=url)
        raise RetryableError("Max retries exceeded")
    except ConnectionError:
        logger.error("Connection error", request_url=url)
        raise RetryableError("Connection error")

    return response
