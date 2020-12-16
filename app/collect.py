from app.publish_dap import send_dap_message
from app.publish_receipt import send_receipt
from app.encryption import decrypt_survey, encrypt_survey
from app.quarantine import quarantine_submission
from app.store import upload_file
from app.transform import transform
from app.validate import validate, ClientError


def process(message):

    print("decrypting...")

    message_data_str = message.data.decode('utf-8')
    survey_dict = decrypt_survey(message_data_str)

    tx_id = extract_tx_id(survey_dict)

    try:

        print("validating...")
        validate(survey_dict)
        print("validation successful")

        print("transforming...")
        transformed_survey = transform(survey_dict)
        print(transformed_survey)

        print("encrypting...")
        encrypted_survey = encrypt_survey(transformed_survey)

        print("write to bucket")

        upload_file(encrypted_survey, tx_id)

        print("receipting...")
        send_receipt(survey_dict)

        print("send dap notification")
        send_dap_message(survey_dict)

    except ClientError as e:
        print(e)
        quarantine_submission(message_data_str, tx_id)


def extract_tx_id(message_dict: dict) -> str:
    return message_dict['tx_id']
