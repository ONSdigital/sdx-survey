import json

from sdx_gcp import RequestsResponse
from sdx_gcp.app import get_logger

from app import sdx_app, CONFIG
from app.deliver import V1, VERSION, TX_ID

logger = get_logger()


def call_legacy_transform(submission: dict, tx_id: str, version: str = V1) -> bytes:
    """
    Makes a call to the transform service and returns the zip
    as bytes or raises the appropriate exception.
    """

    logger.info("Transforming...")
    survey_json = json.dumps(submission)
    endpoint = "transform"
    response: RequestsResponse = sdx_app.http_post(CONFIG.TRANSFORM_SERVICE_URL,
                                                   endpoint,
                                                   survey_json,
                                                   params={VERSION: version, TX_ID: tx_id})

    return response.content
