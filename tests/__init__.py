import io
import json
import zipfile

from app.definitions.submission import SurveySubmission
from app.response import Response

responseTestDataMap = {
    "submission": "original/submission.json",
    "feedback": "original/feedback.json",
    "survey_v1_001": "payload_v1/surveyresponse_0_0_1.json",
    "feedback_v1_001": "payload_v1/feedback_0_0_1.json",
    "survey_v2_001": "payload_v2/business/surveyresponse_0_0_1.json",
    "feedback_v2_001": "payload_v2/business/feedback_0_0_1.json",
    "survey_adhoc_001": "payload_v2/adhoc/surveyresponse_0_0_1.json",
    "feedback_adhoc_001": "payload_v2/adhoc/feedback_0_0_1.json",
}


def get_json(name: str) -> SurveySubmission:
    file = responseTestDataMap.get(name)
    if not file:
        raise ValueError
    path = f'tests/submissions/{file}'
    with open(path) as f:
        data = json.load(f)

    return data


def get_response(name: str) -> Response:
    data = get_json(name)
    # Should probably pass in tx_id, but this will do
    return Response(data, "123")


def unzip(data_bytes: bytes) -> dict[str, bytes]:
    # Create a BytesIO object from the bytes
    zip_file = io.BytesIO(data_bytes)
    results: dict[str, bytes] = {}

    # Open the zip file
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        # List the filenames of the zip file
        for name in zip_ref.namelist():
            results[name] = zip_ref.read(name)

    return results
