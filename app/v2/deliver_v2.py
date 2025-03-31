from typing import Final

from sdx_gcp.app import get_logger

from app import sdx_app, CONFIG

# Constants used within the http request
from app.v2.context import Context


FILE_NAME: Final[str] = "filename"
ZIP_FILE: Final[str] = 'zip_file'
CONTEXT: Final[str] = 'context'
TX_ID: Final[str] = 'tx_id'
ENDPOINT: Final[str] = "deliver/v2/survey"


logger = get_logger()


def deliver_zip(tx_id: str, zipped_file: bytes, context: Context):
    """
    Calls the sdx-deliver endpoint specified by the output_type parameter.
    Returns True or raises appropriate error on response.
    """

    # filename will always be transaction id
    filename = tx_id
    endpoint = ENDPOINT

    sdx_app.http_post(CONFIG.DELIVER_SERVICE_URL,
                      endpoint,
                      None,
                      params={FILE_NAME: filename, TX_ID: tx_id, CONTEXT: context},
                      files={ZIP_FILE: zipped_file})
    return True
