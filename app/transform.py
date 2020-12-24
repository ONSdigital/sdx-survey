import json
import logging

import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.exceptions import MaxRetryError
from structlog import wrap_logger

from app import TRANSFORM_SERVICE_URL
from app.errors import RetryableError, QuarantinableError

logger = wrap_logger(logging.getLogger(__name__))

session = requests.Session()
retries = Retry(total=5, backoff_factor=0.1)
session.mount('http://', HTTPAdapter(max_retries=retries))


def transform(survey_dict: dict):
    logger.info("transforming...")
    survey_json = json.dumps(survey_dict)
    response = post(survey_json)

    if response.status_code == 200:
        return response.content
    elif 400 <= response.status_code < 500:
        msg = "Bad Request response from sdx-transform"
        logger.info(msg)
        raise QuarantinableError(msg)
    else:
        msg = "Bad response from sdx-transform"
        logger.info(msg)
        raise RetryableError(msg)


def post(survey_json):
    url = f"http://{TRANSFORM_SERVICE_URL}/transform"
    logger.info(f"calling {url}")
    try:
        response = session.post(url, survey_json)
    except MaxRetryError:
        logger.error("Max retries exceeded", request_url=url)
        raise RetryableError("Max retries exceeded")
    except ConnectionError:
        logger.error("Connection error", request_url=url)
        raise RetryableError("Connection error")

    return response
