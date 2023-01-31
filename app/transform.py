import json

import requests
import structlog
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.exceptions import MaxRetryError
from requests.exceptions import ConnectionError

from app import CONFIG
from app.deliver import V1, VERSION
from app.errors import RetryableError, QuarantinableError

logger = structlog.get_logger()

session = requests.Session()
retries = Retry(total=5, backoff_factor=0.1)
session.mount('http://', HTTPAdapter(max_retries=retries))


def transform(submission: dict, version: str = V1) -> bytes:
    """
    Makes a call to the transform service and returns the zip
    as bytes or raises the appropriate exception.
    """

    logger.info("Transforming...")
    survey_json = json.dumps(submission)
    response = post(survey_json, version)

    if response.status_code == 200:
        return response.content
    else:
        msg = "Bad response from sdx-transform"
        logger.error(msg, status_code=response.status_code)
        raise QuarantinableError(msg)


def post(survey_json, version):
    """Constructs the http call to the transform service endpoint and posts the request"""

    url = f"http://{CONFIG.TRANSFORM_SERVICE_URL}/transform"
    logger.info(f"Calling {url}")
    try:
        response = session.post(url, survey_json, params={VERSION: version})
    except MaxRetryError:
        logger.error("Max retries exceeded", request_url=url)
        raise RetryableError("Max retries exceeded")
    except ConnectionError:
        logger.error("Connection error", request_url=url)
        raise RetryableError("Connection error")

    return response
