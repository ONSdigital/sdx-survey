import json

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


def get_data(name: str) -> dict:
    file = responseTestDataMap.get(name)
    if not file:
        raise ValueError
    path = f'tests/submissions/{file}'
    with open(path) as f:
        data = json.load(f)
    return data
