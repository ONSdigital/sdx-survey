import json
import logging

import requests
from structlog import wrap_logger

from app import TRANSFORM_SERVICE_URL

logger = wrap_logger(logging.getLogger(__name__))
session = requests.Session()


def transform(survey: dict):
    """ call the transform endpoint and raise quarantinable error if bad response"""
    endpoint = f"http://{TRANSFORM_SERVICE_URL}/transform"
    logger.info("Calling transform", request_url=endpoint)

    response = call_transform_endpoint(survey, endpoint)

    if response_ok(response) and response.content is not None:
        logger.info("Successfully transformed")
        print(type(response.content))
        return response.content

    raise requests.ConnectionError("Response missing content")


def call_transform_endpoint(survey_dict, url):
    # logger trying
    survey_json = json.dumps(survey_dict)
    response = session.post(url, survey_json)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        # logger failed
        raise requests.ConnectionError(response)

    # logger success
    return response


def response_ok(response):
    service = 'SDX transform'

    if response.status_code == 200:
        logger.info("Returned from service", request_url=response.url, status=response.status_code, service=service)
        return True
    elif response.status_code == 404:
        logger.info("Not Found response returned from service",
                    request_url=response.url,
                    status=response.status_code,
                    service=service,
                    )
        raise requests.ConnectionError(f"Not Found response returned from {service}")
    elif 400 <= response.status_code < 500:
        logger.info("Bad Request response from service",
                    request_url=response.url,
                    status=response.status_code,
                    service=service,
                    )
        raise requests.ConnectionError(f"Bad Request response from {service}")

    logger.info("Bad response from service",
                request_url=response.url,
                status=response.status_code,
                service=service,
                )
    raise requests.ConnectionError(f"Bad response from {service}")
