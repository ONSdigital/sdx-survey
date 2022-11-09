import json
import structlog

from app import CONFIG
from app.errors import QuarantinableError
from app.submission_type import get_survey_type, SurveyType

logger = structlog.get_logger()


def send_receipt(survey_dict: dict):
    """Creates and publishes a receipt to the receipt topic"""

    logger.info("Receipting...")
    tx_id = survey_dict['tx_id']

    if get_survey_type(survey_dict) == SurveyType.ADHOC:
        receipt_str: str = make_srm_receipt(survey_dict)
        topic_path: str = CONFIG.RECEIPT_TOPIC_PATH
    else:
        receipt_str: str = make_receipt(survey_dict)
        topic_path: str = CONFIG.RECEIPT_TOPIC_PATH

    publish_data(receipt_str, tx_id, topic_path)
    logger.info('Successfully Receipted')


def publish_data(receipt_str: str, tx_id: str, topic_path: str) -> str:
    """Publishes the receipt to the receipt topic located at topic_path"""

    logger.info('Publishing receipt')
    data = receipt_str.encode("utf-8")
    future = CONFIG.RECEIPT_PUBLISHER.publish(topic_path, data, tx_id=tx_id)
    return future.result()


def make_receipt(survey_dict: dict) -> str:
    """Creates a receipt for RASRM"""

    try:
        receipt_json = {
            'caseId': survey_dict['case_id'],
            'partyId': survey_dict['metadata']['user_id']
        }
    except KeyError as e:
        raise QuarantinableError(f'Failed to make receipt: {str(e)}')

    logger.info('Generated receipt', caseId=receipt_json['caseId'], partyId=receipt_json['partyId'])
    receipt_str = json.dumps(receipt_json)
    return receipt_str


def make_srm_receipt(survey_dict: dict) -> str:
    """Creates a receipt for SRM"""

    try:
        receipt_json = {
            'qid': survey_dict['survey_metadata']['qid']
        }
    except KeyError as e:
        raise QuarantinableError(f'Failed to make receipt: {str(e)}')

    logger.info('Generated SRM receipt', qid=receipt_json['qid'])
    receipt_str = json.dumps(receipt_json)
    return receipt_str
