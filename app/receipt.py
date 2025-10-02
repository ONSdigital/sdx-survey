import json

from sdx_base.errors.errors import DataError

from app import CONFIG, get_logger
from app.response import Response, SurveyType

logger = get_logger()


def send_receipt(response: Response):
    """Creates and publishes a receipt to the receipt topic"""

    logger.info("Receipting...")
    tx_id = response.get_tx_id()

    if response.get_survey_type() == SurveyType.ADHOC:
        receipt_str: str = make_srm_receipt(response)
        topic_path: str = CONFIG.SRM_RECEIPT_TOPIC_PATH
    else:
        receipt_str: str = make_receipt(response)
        topic_path: str = CONFIG.RECEIPT_TOPIC_PATH

    publish_data(receipt_str, tx_id, topic_path)
    logger.info('Successfully Receipted')


def publish_data(receipt_str: str, tx_id: str, topic_path: str) -> str:
    """Publishes the receipt to the receipt topic located at topic_path"""

    logger.info('Publishing receipt')
    result = publish_message(topic_path, receipt_str, {"tx_id": tx_id})
    return result


def make_receipt(response: Response) -> str:
    """Creates a receipt for RASRM"""

    try:
        receipt_json = {
            'caseId': response.get_case_id(),
            'partyId': response.get_user_id()
        }
    except KeyError as e:
        raise DataError(f'Failed to make receipt: {str(e)}')

    logger.info('Generated receipt', extra={"caseId": receipt_json['caseId'], "partyId":receipt_json['partyId']})
    receipt_str = json.dumps(receipt_json)
    return receipt_str


def make_srm_receipt(response: Response) -> str:
    """Creates a receipt for SRM"""

    try:
        receipt_json = {
            'data': {
                'qid': response.get_qid()
            }
        }
    except KeyError as e:
        raise DataError(f'Failed to make receipt: {str(e)}')

    logger.info('Generated SRM receipt', extra={"qid": receipt_json['data']})
    receipt_str = json.dumps(receipt_json)
    return receipt_str
