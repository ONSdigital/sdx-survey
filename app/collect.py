import json

from app.publish_dap import send_dap_message
from app.publish_receipt import send_receipt
from app.encryption import decrypt_survey, encrypt_survey
from app.store import upload_file


def process(message):

    print("decrypting...")

    message_data_str = message.data.decode('utf-8')
    survey_dict = decrypt_survey(message_data_str)

    print("validating...")

    print("transforming...")

    print("encrypting...")
    encrypted_survey = encrypt_survey(survey_dict)

    print("write to bucket")

    tx_id = extract_tx_id(survey_dict)
    upload_file(encrypted_survey, tx_id)

    print("receipting...")
    send_receipt(survey_dict)

    print("send dap notification")
    send_dap_message(survey_dict)


def extract_tx_id(message_dict: dict) -> str:
    return message_dict['tx_id']
