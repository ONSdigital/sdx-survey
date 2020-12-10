from app import dap_publisher, dap_topic_path
import hashlib
import json
from datetime import datetime


def send_dap_message(survey_dict):
    message = create_dap_message(survey_dict)
    publish_data(message)


def publish_data(data_str):
    # Data must be a bytestring
    data = data_str.encode("utf-8")
    # When you publish a message, the client returns a future.
    future = dap_publisher.publish(dap_topic_path, data)
    return future.result()


def create_dap_message(survey_dict: dict) -> str:
    survey_json = json.dumps(survey_dict)
    survey_bytes = survey_json.encode("utf-8")
    md5_hash = hashlib.md5(survey_bytes).hexdigest()

    try:
        description = "{} survey response for period {} sample unit {}".format(
            survey_dict['survey_id'],
            survey_dict['collection']['period'],
            survey_dict['metadata']['ru_ref'])
        dap_message = {
            'version': '1',
            'files': [{
                'name': f"{survey_dict['tx_id']}.json",
                'URL': f"http://sdx-store:5000/responses/{survey_dict['tx_id']}",
                'sizeBytes': len(survey_bytes),
                'md5sum': md5_hash
            }],
            'sensitivity': 'High',
            'sourceName': 'sdx-development',
            'manifestCreated': get_formatted_current_utc(),
            'description': description,
            'iterationL1': survey_dict['collection']['period'],
            'dataset': survey_dict['survey_id'],
            'schemaversion': '1'
        }
    except KeyError:
        # self.logger.exception("Unsuccesful publish, missing key values")
        # raise QuarantinableError
        print("failed to produce dap message!")

    print("Created dap data")
    return json.dumps(dap_message)


def get_formatted_current_utc():
    """
    Returns a formatted utc date with only 3 milliseconds as opposed to the ususal 6 that python provides.
    Additionally, we provide the Zulu time indicator (Z) at the end to indicate it being UTC time. This is
    done for consistency with timestamps provided in other languages.
    The format the time is returned is YYYY-mm-ddTHH:MM:SS.fffZ (e.g., 2018-10-10T08:42:24.737Z)
    """
    date_time = datetime.utcnow()
    milliseconds = date_time.strftime("%f")[:3]
    return f"{date_time.strftime('%Y-%m-%dT%H:%M:%S')}.{milliseconds}Z"
