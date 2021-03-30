import json

import requests
import structlog

from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.exceptions import MaxRetryError
from requests.exceptions import ConnectionError
from structlog.contextvars import bind_contextvars

from app import CONFIG
from app.errors import QuarantinableError, RetryableError

DAP = "dap"
LEGACY = "legacy"
FEEDBACK = "feedback"
SUBMISSION_FILE = 'submission'
TRANSFORMED_FILE = 'transformed'
UTF8 = "utf-8"

logger = structlog.get_logger()

session = requests.Session()
retries = Retry(total=5, backoff_factor=0.1)
session.mount('http://', HTTPAdapter(max_retries=retries))


def deliver_dap(survey_dict: dict):
    logger.info("Sending DAP submission")
    deliver(survey_dict, DAP)


def deliver_survey(survey_dict: dict, zip_file: bytes):
    logger.info("Sending survey submission")
    files = {TRANSFORMED_FILE: zip_file}
    deliver(survey_dict, LEGACY, files)


def deliver_feedback(survey_dict: dict):
    logger.info(f"Sending feedback submission")
    deliver(survey_dict, FEEDBACK)


def deliver(survey_dict: dict, output_type: str, files: dict = {}):
    survey_id = survey_dict['survey_id']
    files[SUBMISSION_FILE] = json.dumps(survey_dict).encode(UTF8)
    response = post(survey_dict['tx_id'], files, output_type)
    status_code = response.status_code
    bind_contextvars(survey_id=survey_id)

    if status_code == 200:
        return True
    elif 400 <= status_code < 500:
        msg = "Bad Request response from sdx-deliver"
        logger.error(msg, status_code=status_code, survey_id=survey_id)
        raise QuarantinableError(msg)
    else:
        msg = "Bad response from sdx-deliver"
        logger.error(msg, status_code=status_code, survey_id=survey_id)
        raise RetryableError(msg)


def post(filename: str, files: dict, output_type: str):
    url = f"http://{CONFIG.DELIVER_SERVICE_URL}/deliver/{output_type}"
    logger.info(f"Calling {url}")
    try:
        response = session.post(url, params={"filename": filename}, files=files)
    except MaxRetryError:
        logger.error("Max retries exceeded", request_url=url)
        raise RetryableError("Max retries exceeded")
    except ConnectionError:
        logger.error("Connection error", request_url=url)
        raise RetryableError("Connection error")

    return response
