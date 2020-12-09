import json
from app.store import upload_file


def process(message):
    print(message.data)

    print("decrypting...")

    print("validating...")

    print("transforming...")

    print("receipting...")

    print("write to bucket")
    upload_file(message.data, extract_tx_id(message))


def extract_tx_id(message):
    message_dict = json.loads(message.data)
    return message_dict['tx_id']
