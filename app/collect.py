from app.publish_dap import send_dap_message
from app.publish_receipt import send_receipt
from app.encryption import decrypt_survey, encrypt_survey, encrypt_zip
from app.quarantine import quarantine_submission
from app.store import upload_file
from app.transform import transform
from app.validate import validate, ClientError

dap_surveys = ["023", "134", "147", "281", "283", "lms", "census"]


def process(message):
    print("decrypting...")

    message_data_str = message.data.decode('utf-8')
    survey_dict = decrypt_survey(message_data_str)

    tx_id = extract_tx_id(survey_dict)

    try:

        print("validating...")
        validate(survey_dict)
        print("validation successful")

        if survey_dict['survey_id'] not in dap_surveys:
            print("transforming...")
            transformed_survey = transform(survey_dict)
            print('encrypting zip....')
            encrypted_survey = encrypt_zip(transformed_survey)
        else:
            print("encrypting...")
            encrypted_survey = encrypt_survey(survey_dict)

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
