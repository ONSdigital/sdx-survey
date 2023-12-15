from sdx_gcp import RequestsResponse
from sdx_gcp.app import get_logger

from app import sdx_app, CONFIG
from app.deliver import V1, VERSION, TX_ID
from app.response import Response

logger = get_logger()


def call_legacy_transform(response: Response, version: str = V1) -> bytes:
    """
    Makes a call to the transform service and returns the zip
    as bytes or raises the appropriate exception.
    """

    logger.info("Transforming...")
    tx_id = response.get_tx_id()
    survey_json = response.to_json()
    endpoint = "transform"
    response: RequestsResponse = sdx_app.http_post(CONFIG.TRANSFORM_SERVICE_URL,
                                                   endpoint,
                                                   survey_json,
                                                   params={VERSION: version, TX_ID: tx_id})

    return response.content
