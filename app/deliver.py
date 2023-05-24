import json

from sdx_gcp.app import get_logger

from app import sdx_app, CONFIG
from app.submission_type import get_tx_id

# Constants used within the http request
DAP = "dap"
LEGACY = "legacy"
HYBRID = "hybrid"
FEEDBACK = "feedback"
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


def deliver_dap(submission: dict[str, str], tx_id: str, version: str = V1):
    """deliver a survey submission intended for DAP"""
    logger.info("Sending DAP submission")
    deliver(submission, DAP, tx_id, version=version)


def deliver_survey(submission: dict[str, str], zip_file: bytes, tx_id: str, version: str = V1):
    """deliver a survey submission intended for the legacy systems"""
    logger.info("Sending survey submission")
    files = {TRANSFORMED_FILE: zip_file}
    deliver(submission, LEGACY, tx_id, files, version=version)


def deliver_hybrid(submission: dict[str, str], zip_file: bytes, tx_id: str, version: str = V1):
    """deliver a survey submission intended for dap and the legacy systems"""
    logger.info("Sending hybrid submission")
    files = {TRANSFORMED_FILE: zip_file}
    deliver(submission, HYBRID, tx_id, files, version=version)


def deliver_feedback(submission: dict[str, str], filename: str, tx_id: str, version: str = V1):
    """deliver a feedback survey submission"""
    logger.info("Sending feedback submission")
    deliver(submission, FEEDBACK, tx_id, {}, filename, version=version)


def deliver(
        submission: dict[str, str],
        output_type: str,
        tx_id: str,
        files: dict[str, bytes] = {},
        filename: str = None,
        version: str = V1):
    """
    Calls the deliver endpoint specified by the output_type parameter.
    Returns True or raises appropriate error on response.
    """
    if not filename:
        filename = get_tx_id(submission)

    files[SUBMISSION_FILE] = json.dumps(submission).encode(UTF8)
    endpoint = f"deliver/{output_type}"
    sdx_app.http_post(CONFIG.DELIVER_SERVICE_URL,
                      endpoint,
                      None,
                      params={FILE_NAME: filename, VERSION: version, TX_ID: tx_id},
                      files=files)
    return True
