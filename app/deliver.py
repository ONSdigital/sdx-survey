import logging

import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.exceptions import MaxRetryError
from requests.exceptions import ConnectionError
from structlog import wrap_logger

from app import DELIVER_SERVICE_URL
from app.errors import QuarantinableError, RetryableError

DELIVER_NAME = 'zip'

logger = wrap_logger(logging.getLogger(__name__))

session = requests.Session()
retries = Retry(total=5, backoff_factor=0.1)
session.mount('http://', HTTPAdapter(max_retries=retries))


def deliver_dap(survey_dict: dict, file_bytes: bytes):
    deliver(survey_dict, file_bytes, 'dap')


def deliver_survey(survey_dict: dict, file_bytes: bytes):
    deliver(survey_dict, file_bytes, 'survey')


def deliver_feedback(survey_dict: dict, file_bytes: bytes):
    deliver(survey_dict, file_bytes, 'feedback')


def deliver(survey_dict: dict, file_bytes: bytes, file_type: str):
    metadata = create_survey_metadata(survey_dict)
    response = post(file_bytes, file_type, metadata)

    if response.status_code == 200:
        return True
    elif 400 <= response.status_code < 500:
        raise QuarantinableError("Bad Request response from sdx-deliver")
    else:
        raise RetryableError("Bad response from sdx-deliver")


def create_survey_metadata(survey_dict: dict) -> dict:
    metadata = {
        'survey_id': survey_dict['survey_id'],
        'description': get_description(survey_dict),
        'iteration': get_iteration(survey_dict)
    }
    return metadata


def get_description(survey_dict: dict) -> str:
    return "{} survey response for period {} sample unit {}".format(
        survey_dict['survey_id'],
        survey_dict['collection']['period'],
        survey_dict['metadata']['ru_ref']
    )


def get_iteration(survey_dict: dict) -> str:
    return survey_dict['collection']['period']


def post(file_bytes, file_type, metadata):
    url = f"http://{DELIVER_SERVICE_URL}/deliver/{file_type}"
    logger.info(f"calling {url}")
    try:
        response = session.post(url, data=metadata, files={DELIVER_NAME: file_bytes})
    except MaxRetryError:
        logger.error("Max retries exceeded", request_url=url)
        raise RetryableError("Max retries exceeded")
    except ConnectionError:
        logger.error("Connection error", request_url=url)
        raise RetryableError("Connection error")

    return response
