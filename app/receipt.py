import json
import structlog

from app import CONFIG
from app.errors import QuarantinableError

logger = structlog.get_logger()


def send_receipt(survey_dict: dict):
    """Creates and publishes a receipt to the receipt topic"""

    logger.info("Receipting...")
    tx_id = survey_dict['tx_id']
    receipt_str = make_receipt(survey_dict)
    publish_data(receipt_str, tx_id)
    logger.info('Successfully Receipted')


def publish_data(receipt_str: str, tx_id: str) -> str:
    """Publishes the receipt to the receipt topic"""

    logger.info('Publishing receipt')
    data = receipt_str.encode("utf-8")
    future = CONFIG.RECEIPT_PUBLISHER.publish(CONFIG.RECEIPT_TOPIC_PATH, data, tx_id=tx_id)
    return future.result()


def make_receipt(survey_dict: dict) -> str:
    """Creates a receipt as String with the required metadata from the survey dict"""

    try:
        receipt_json = {
            'case_id': survey_dict['case_id'],
            'tx_id': survey_dict['tx_id'],
            'collection': {
                'exercise_sid':
                    survey_dict['collection']['exercise_sid']
            },
            'metadata': {
                'ru_ref': survey_dict['metadata']['ru_ref'],
                'user_id': survey_dict['metadata']['user_id']
            }
        }
    except KeyError as e:
        raise QuarantinableError(f'Failed to make receipt: {str(e)}')

    receipt_str = json.dumps(receipt_json)
    return receipt_str
