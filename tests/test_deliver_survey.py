import unittest
import json
from unittest import mock
from app.errors import QuarantinableError, RetryableError

from app import deliver

dap_data = '''{  
   "origin":"uk.gov.ons.edc.eq",
   "survey_id":"134",
   "tx_id":"40e659ec-013f-4993-9a31-ec1e0ad37888",
   "case_id": "4c0bc9ec-06d4-4f66-88b6-2e42b79f17b3",
   "data":{  
      "133w":"Weekly",
      "134f":"Fortnightly",
      "130":"Calendar monthly",
      "131":"Four weekly",
      "132":"Five weekly",
      "40":"5",
      "50":"445566",
      "60":"112233",
      "70":"334455",
      "80":"556677",
      "90w":"Yes",
      "91w":"Yes",
      "92w":"Fewer temporary staff",
      "93w":"Yes",
      "94w":"More overtime",
      "95w":"Yes",
      "100":"50",
      "110":"01/02/2016",
      "120":"25",
      "96w":"Yes",
      "97w":"Yes",
      "300w":"Pipe mania",
      "40f":"10",
      "50f":"123123",
      "60f":"456456",
      "80f":"101010",
      "70f":"789789",
      "90f":"Yes",
      "91f":"Yes",
      "92f":"Fewer temporary staff",
      "93f":"Yes",
      "94f":"More overtime",
      "95f":"Yes",
      "110f":"02/03/2017",
      "100f":"60",
      "120f":"30",
      "96f":"Yes",
      "97f":"Yes",
      "300f":"Gas leak",
      "140m":"20",
      "151":"321321",
      "181":"999999",
      "171":"121212",
      "190m":"Yes",
      "191m":"Yes",
      "192m":"Fewer temporary staff",
      "193m":"Yes",
      "194m":"More overtime",
      "195m":"Yes",
      "210":"03/04/2018",
      "200":"70",
      "220":"40",
      "196m":"Yes",
      "197m":"Yes",
      "300m":"copper pipe",
      "140w4":"30",
      "152":"98765",
      "172":"443322",
      "182":"767676",
      "190w4":"Yes",
      "191w4":"Yes",
      "192w4":"Fewer temporary staff",
      "193w4":"Yes",
      "194w4":"More overtime",
      "195w4":"Yes",
      "200w4":"80",
      "210w4":"04/05/2019",
      "220w4":"50",
      "196w4":"Yes",
      "197w4":"Yes",
      "300w4":"solder joint",
      "140w5":"40",
      "153":"13134",
      "173":"989",
      "183":"9112",
      "190w5":"Yes",
      "191w5":"Yes",
      "192w5":"Fewer temporary staff",
      "193w5":"Yes",
      "194w5":"More overtime",
      "195w5":"Yes",
      "200w5":"90",
      "220w5":"60",
      "210w5":"05/06/2020",
      "196w5":"Yes",
      "197w5":"Yes",
      "300w5":"drill hole",
      "300":"flux clean"
   },
   "type":"uk.gov.ons.edc.eq:surveyresponse",
   "version":"0.0.1",
   "metadata":{  
      "user_id":"K5O86M2NU1",
      "ru_ref":"12346789012A"
   },
   "started_at":"2017-03-01T13:00:46.101447+00:00",
   "submitted_at":"2017-03-01T14:25:46.101447+00:00",
   "collection":{  
      "period":"201605",
      "exercise_sid":"82R1VDWN74",
      "instrument_id":"0005"
   }
}
'''
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


def status_code_success(file_bytes, file_type, metadata):
    return ResponseCodes(200)


def status_code_fail(file_bytes, file_type, metadata):
    return ResponseCodes(400)


class ResponseCodes:
    def __init__(self, number):
        self.status_code = number


class TestDeliver(unittest.TestCase):
    @mock.patch('app.deliver.post', side_effect=status_code_success)
    def test_deliver_submission_success(self, mock_post):
        dap_dict = json.loads(dap_data)
        dap_bytes = json.dumps(dap_dict).encode("utf-8")
        deliver_dap = deliver.deliver(dap_dict, dap_bytes, 'dap')

        survey_dict = json.loads(survey_data)
        survey_bytes = json.dumps(survey_dict).encode("utf-8")
        deliver_survey = deliver.deliver(survey_dict, survey_bytes, 'survey')

        feedback_dict = json.loads(feedback_data)
        feedback_bytes = json.dumps(feedback_dict).encode("utf-8")
        deliver_feedback = deliver.deliver(feedback_dict, feedback_bytes, 'feedback')
        self.assertTrue(deliver_dap)
        self.assertTrue(deliver_survey)
        self.assertTrue(deliver_feedback)

    @mock.patch('app.deliver.post', side_effect=status_code_fail)
    def test_deliver_submission_failure(self, mock_post):
        with self.assertRaises(QuarantinableError) as dap_exception:
            dap_dict = json.loads(dap_data)
            dap_bytes = json.dumps(dap_dict).encode("utf-8")
            deliver.deliver(dap_dict, dap_bytes, 'dap')
        dap_exception_str = str(dap_exception.exception)
        self.assertEqual(dap_exception_str, "Bad Request response from sdx-deliver")

        with self.assertRaises(QuarantinableError) as survey_exception:
            survey_dict = json.loads(survey_data)
            survey_bytes = json.dumps(survey_dict).encode("utf-8")
            deliver.deliver(survey_dict, survey_bytes, 'survey')
        survey_exception_str = str(survey_exception.exception)
        self.assertEqual(survey_exception_str, "Bad Request response from sdx-deliver")

        with self.assertRaises(QuarantinableError) as feedback_exception:
            feedback_dict = json.loads(feedback_data)
            feedback_bytes = json.dumps(feedback_dict).encode("utf-8")
            deliver.deliver(feedback_dict, feedback_bytes, 'feedback')
        feedback_exception_str = str(feedback_exception.exception)
        self.assertEqual(feedback_exception_str, "Bad Request response from sdx-deliver")




