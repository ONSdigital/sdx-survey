import json

from sdx_gcp.app import get_logger
from sdx_gcp.errors import DataError
from sdx_gcp.pubsub import publish_message

from app import CONFIG
from app.submission_type import get_survey_type, SurveyType, get_tx_id, get_user_id, get_case_id

logger = get_logger()


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
    result = publish_message(topic_path, receipt_str, {"tx_id": tx_id})
    return result


def make_receipt(submission: dict) -> str:
    """Creates a receipt for RASRM"""

    try:
        receipt_json = {
            'caseId': get_case_id(submission),
            'partyId': get_user_id(submission)
        }
    except KeyError as e:
        raise DataError(f'Failed to make receipt: {str(e)}')

    logger.info('Generated receipt', caseId=receipt_json['caseId'], partyId=receipt_json['partyId'])
    receipt_str = json.dumps(receipt_json)
    return receipt_str


def make_srm_receipt(submission: dict) -> str:
    """Creates a receipt for SRM"""

    try:
        receipt_json = {
            'data': {
                'qid': submission['survey_metadata']['qid']
            }
        }
    except KeyError as e:
        raise DataError(f'Failed to make receipt: {str(e)}')

    logger.info('Generated SRM receipt', qid=receipt_json['data'])
    receipt_str = json.dumps(receipt_json)
    return receipt_str
