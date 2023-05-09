import json
import time

import requests
import google.auth.transport.requests
import google.oauth2.id_token
import structlog

from app import CONFIG
from app.deliver import V1, VERSION
from app.errors import RetryableError, QuarantinableError

logger = structlog.get_logger()


def transform(submission: dict, version: str = V1) -> bytes:
    """
    Makes a call to the transform service and returns the zip
    as bytes or raises the appropriate exception.
    """

    logger.info("Transforming...")
    survey_json = json.dumps(submission)

    trying = True
    retries = 0
    max_retries = 3
    http_response = None

    while trying:
        try:
            http_response = post(survey_json, version)
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
            return http_response.content
        elif 400 <= status_code < 500:
            msg = f"Bad response from sdx-transform: {http_response.reason}"
            logger.error(msg, status_code=http_response.status_code)
            raise QuarantinableError(msg)
        else:
            msg = f"Bad response from sdx-transform: {http_response.reason}"
            logger.error(msg, status_code=http_response.status_code)
            raise RetryableError(msg)
    else:
        msg = f"No response from sdx-transform!"
        logger.error(msg)
        raise RetryableError(msg)


def post(survey_json, version):
    """Constructs the http call to the transform service endpoint and posts the request"""
    audience = CONFIG.TRANSFORM_SERVICE_URL
    endpoint = f"{audience}/transform"
    auth_req = google.auth.transport.requests.Request()
    id_token = google.oauth2.id_token.fetch_id_token(auth_req, audience)
    logger.info(f"Calling {endpoint}")

    try:
        response = requests.post(
            endpoint,
            survey_json,
            params={VERSION: version},
            headers={"Authorization": f"Bearer {id_token}"}
        )

    except Exception:
        logger.error("Connection error", request_url=endpoint)
        raise RetryableError("Connection error")

    return response
