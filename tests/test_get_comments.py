import json
import unittest
from app.comments import store_comments


class TestGetComments(unittest.TestCase):

    def test_comments(self):
        data = '''{
        "collection": {
            "exercise_sid": "XxsteeWv",
            "instrument_id": "0167",
            "period": "1704"
        },
        "data": {
            "46": "123",
            "47": "456",
            "50": "789",
            "51": "111",
            "52": "222",
            "53": "333",
            "54": "444",
            "146": "This is a comment on how this survey service went.",
            "d12": "Yes",
            "d40": "Yes"
        },
        "flushed": false,
        "metadata": {
            "ref_period_end_date": "2016-05-31",
            "ref_period_start_date": "2016-05-01",
            "ru_ref": "49900108249D",
            "user_id": "UNKNOWN"
        },
        "origin": "uk.gov.ons.edc.eq",
        "started_at": "2017-07-05T10:54:11.548611+00:00",
        "submitted_at": "2017-07-05T14:49:33.448608+00:00",
        "type": "uk.gov.ons.edc.eq:surveyresponse",
        "version": "0.0.1",
        "survey_id": "009",
        "tx_id": "c37a3efa-593c-4bab-b49c-bee0613c4fb4",
        "case_id": "4c0bc9ec-06d4-4f66-88b6-2e42b79f17b3"
    }'''
        submission = json.loads(data)
        actual = store_comments(submission)
        expected = "This is a comment on how this survey service went."
        self.assertEqual(expected, actual)
