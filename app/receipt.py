import json
import logging

from structlog import wrap_logger

from app import receipt_publisher, receipt_topic_path
from app.errors import ClientError

logger = wrap_logger(logging.getLogger(__name__))


def send_receipt(survey_dict: dict) -> str:
    logger.info("receipting...")
    tx_id = survey_dict['tx_id']
    receipt_str = make_receipt(survey_dict)
    publish_data(receipt_str, tx_id)
    print('Successfully Receipted')


def publish_data(receipt_str: str, tx_id: str) -> str:
    print('publishing receipt')
    data = receipt_str.encode("utf-8")
    future = receipt_publisher.publish(receipt_topic_path, data, tx_id=tx_id)
    return future.result()


def make_receipt(survey_dict: dict) -> str:
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
        raise ClientError(str(e))

    receipt_str = json.dumps(receipt_json)
    return receipt_str
