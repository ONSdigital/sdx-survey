import json
from app import receipt_publisher, receipt_topic_path


def send_receipt(survey_dict: dict):
    receipt_str = make_receipt(survey_dict)
    publish_data(receipt_str)


def publish_data(data):
    # Data must be a bytestring
    data = data.encode("utf-8")
    # When you publish a message, the client returns a future.
    future = receipt_publisher.publish(receipt_topic_path, data)
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
    except KeyError:
        print('failed to receipt')

    receipt_str = json.dumps(receipt_json)
    return receipt_str
