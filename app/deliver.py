
from sdx_gcp.app import get_logger

from app import sdx_app, CONFIG
from app.response import Response

# Constants used within the http request
DAP = "dap"
LEGACY = "legacy"
HYBRID = "hybrid"
FEEDBACK = "feedback"
SPP = "spp"
SUBMISSION_FILE = 'submission'
TRANSFORMED_FILE = 'transformed'
UTF8 = "utf-8"
FILE_NAME = "filename"
VERSION = "version"
TX_ID = "tx_id"
V1 = "v1"
V2 = "v2"
ADHOC = "adhoc"

logger = get_logger()


def deliver_dap(response: Response, version: str = V1):
    """deliver a survey submission intended for DAP"""
    logger.info("Sending DAP submission")
    deliver(response, DAP, {}, version=version)


def deliver_survey(response: Response, zip_file: bytes, version: str = V1):
    """deliver a survey submission intended for the legacy systems"""
    logger.info("Sending survey submission")
    files = {TRANSFORMED_FILE: zip_file}
    deliver(response, LEGACY, files, version=version)


def deliver_hybrid(response: Response, zip_file: bytes, version: str = V1):
    """deliver a survey submission intended for dap and the legacy systems"""
    logger.info("Sending hybrid submission")
    files = {TRANSFORMED_FILE: zip_file}
    deliver(response, HYBRID, files, version=version)


def deliver_feedback(response: Response, version: str = V1):
    """deliver a feedback survey submission"""
    logger.info("Sending feedback submission")
    deliver(response, FEEDBACK, {}, version=version)


def deliver(response: Response, output_type: str, files: dict[str, bytes], version: str = V1):
    """
    Calls the sdx-deliver endpoint specified by the output_type parameter.
    Returns True or raises appropriate error on response.
    """

    tx_id = response.get_tx_id()

    filename = tx_id

    if version == V1:
        submission_json = response.to_v1_json()
    else:
        submission_json = response.to_json()

    files[SUBMISSION_FILE] = submission_json.encode(UTF8)

    endpoint = f"deliver/{output_type}"
    sdx_app.http_post(CONFIG.DELIVER_SERVICE_URL,
                      endpoint,
                      None,
                      params={FILE_NAME: filename, VERSION: version, TX_ID: tx_id},
                      files=files)
    return True
