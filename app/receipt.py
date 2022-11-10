import json
import structlog

from app import CONFIG
from app.errors import QuarantinableError
from app.submission_type import get_survey_type, SurveyType, get_tx_id, get_user_id, get_case_id

logger = structlog.get_logger()


def send_receipt(submission: dict):
    """Creates and publishes a receipt to the receipt topic"""

    logger.info("Receipting...")
    tx_id = get_tx_id(submission)

    if get_survey_type(submission) == SurveyType.ADHOC:
        receipt_str: str = make_srm_receipt(submission)
        topic_path: str = CONFIG.SRM_RECEIPT_TOPIC_PATH
    else:
        receipt_str: str = make_receipt(submission)
        topic_path: str = CONFIG.RECEIPT_TOPIC_PATH

    publish_data(receipt_str, tx_id, topic_path)
    logger.info('Successfully Receipted')


def publish_data(receipt_str: str, tx_id: str, topic_path: str) -> str:
    """Publishes the receipt to the receipt topic located at topic_path"""

    logger.info('Publishing receipt')
    data = receipt_str.encode("utf-8")
    future = CONFIG.RECEIPT_PUBLISHER.publish(topic_path, data, tx_id=tx_id)
    return future.result()


def make_receipt(submission: dict) -> str:
    """Creates a receipt for RASRM"""

    try:
        receipt_json = {
            'caseId': get_case_id(submission),
            'partyId': get_user_id(submission)
        }
    except KeyError as e:
        raise QuarantinableError(f'Failed to make receipt: {str(e)}')

    logger.info('Generated receipt', caseId=receipt_json['caseId'], partyId=receipt_json['partyId'])
    receipt_str = json.dumps(receipt_json)
    return receipt_str


def make_srm_receipt(submission: dict) -> str:
    """Creates a receipt for SRM"""

    try:
        receipt_json = {
            'qid': submission['survey_metadata']['qid']
        }
    except KeyError as e:
        raise QuarantinableError(f'Failed to make receipt: {str(e)}')

    logger.info('Generated SRM receipt', qid=receipt_json['qid'])
    receipt_str = json.dumps(receipt_json)
    return receipt_str
