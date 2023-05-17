import json

from sdx_gcp import Response
from sdx_gcp.app import get_logger

from app import sdx_app, CONFIG
from app.deliver import V1, VERSION

logger = get_logger()


def transform(submission: dict, version: str = V1) -> bytes:
    """
    Makes a call to the transform service and returns the zip
    as bytes or raises the appropriate exception.
    """

    logger.info("Transforming...")
    survey_json = json.dumps(submission)
    endpoint = f"transform"
    response: Response = sdx_app.http_post(CONFIG.TRANSFORM_SERVICE_URL,
                                           endpoint,
                                           survey_json,
                                           params={VERSION: version})

    return response.content
