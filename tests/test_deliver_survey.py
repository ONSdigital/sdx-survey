import unittest
import json
import requests
from unittest import mock

from app.deliver import deliver

dap_data = '''{
    "type": "uk.gov.ons.edc.eq:surveyresponse",
    "version": "0.0.1",
    "origin": "uk.gov.ons.edc.eq",
    "survey_id": "023",
    "case_id": "4c0bc9ec-06d4-4f66-88b6-2e42b79f17b3",
    "collection": {
        "exercise_sid": "hfjdskf",
        "instrument_id": "0112",
        "period": "1604"
    },
    "started_at": "2016-03-11T12:01:26Z",
    "submitted_at": "2016-03-12T13:01:26Z",
    "metadata": {
        "user_id": "789473423",
        "ru_ref": "12345678901A"
    },
    "data": {
        "11": "1/4/2016",
        "12": "31/10/2016",
        "51": "84",
        "52": "10",
        "53": "73",
        "54": "24",
        "50": "205",
        "20": "1800000",
        "21": "60000",
        "146": "Change comments included",
        "147": "An employee comment for 0112"
    }
}'''
survey_data = '''{
    "case_id": "d7ef5c5e-efa9-48b2-847e-ec41e925f7dc",
    "collection": {
        "exercise_sid": "664dbdf4-02fb-4d68-b0cf-7f7402df00e5",
        "instrument_id": "0012",
        "period": "201904"
    },
    "data": {
        "15": "No",
        "119": "1250",
        "120": "1554",
        "144": "28250",
        "145": "30124",
        "146": "This is a comment"
    },
    "flushed": false,
    "metadata": {
        "ref_period_end_date": "2019-01-02",
        "ref_period_start_date": "2019-04-01",
        "ru_ref": "25462342626B",
        "user_id": "UNKNOWN"
    },
    "origin": "uk.gov.ons.edc.eq",
    "started_at": "2019-04-01T14:00:24.224709",
    "submitted_at": "2019-04-01T14:10:26.933601",
    "survey_id": "017",
    "tx_id": "76de5870-8ec7-4750-b523-2142e9154c47",
    "type": "uk.gov.ons.edc.eq:surveyresponse",
    "version": "0.0.1"
}'''
feedback_data = '''{
    "data": {
        "url": "https://eq.ons.gov.uk/questionnaire/lms/2/3c5b8eb9-17e9-493e-a5d4-d4eacee79309/household-member-group/0/paid-job-q1",
        "name": "Another Person",
        "email": "a.person@email.com",
        "message": "I think this page is quite good"
    },
    "type": "uk.gov.ons.edc.eq:feedback",
    "tx_id": "7c3dda82-a274-40dd-84f1-7ed08b7a917e",
    "origin": "uk.gov.ons.edc.eq",
    "version": "0.0.1",
    "metadata": {
        "ru_ref": "ABC123456",
        "user_id": "a7b481f5-be36-484b-b7e5-61a2d90f10ee"
    },
    "survey_id": "lms",
    "collection": {
        "period": "2",
        "exercise_sid": "3c5b8eb9-17e9-493e-a5d4-d4eacee79309",
        "instrument_id": "2"
    },
    "submitted_at": "2018-10-27T10:12:14.257090"
}'''


class TestDeliver(unittest.TestCase):

    def test_deliver_submission_success(self):
        survey_dict = json.loads(survey_data)
        feedback_dict = json.loads(feedback_data)
        dap_dict = json.loads(dap_data)
        r = requests.Response()
        with mock.patch('requests.post') as mock_post:
            mock_post.return_value = r
            r.status_code = 200
            response = deliver.deliver_dap(dap_dict)
            self.assertEqual(response.status_code, 200)

