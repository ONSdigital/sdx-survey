import json

from app.publish_dap import send_dap_message
from app.publish_receipt import send_receipt
from app.encryption import decrypt_survey, encrypt_survey
from app.store import upload_file


def process(message):
    print(message.data)

    print("decrypting...")

    message_data_str = message.data.decode('utf-8')
    print(type(message_data_str))
    survey_dict = decrypt_survey(message_data_str)

    print("validating...")

    print("transforming...")

    print("encrypting...")
    encrypted_survey = encrypt_survey(survey_dict)

    print("write to bucket")
    upload_file(encrypted_survey, extract_tx_id(message))

    print("receipting...")
    send_receipt(survey_dict)

    print("send dap notification")
    send_dap_message(survey_dict)


def extract_tx_id(message):
    message_dict = json.loads(message.data)
    return message_dict['tx_id']
