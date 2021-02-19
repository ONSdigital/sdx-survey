import unittest
import json
import requests
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

dap_metadata = '''{"filename": "40e659ec-013f-4993-9a31-ec1e0ad37888", "tx_id": "40e659ec-013f-4993-9a31-ec1e0ad37888", "survey_id": "134", "description": "134 survey response for period 201605 sample unit 12346789012A", "iteration": "201605"}'''
survey_metadata = '''{"filename": "76de5870-8ec7-4750-b523-2142e9154c47", "tx_id": "76de5870-8ec7-4750-b523-2142e9154c47", "survey_id": "017", "description": "017 survey response for period 201904 sample unit 25462342626B", "iteration": "201904"}'''
feedback_metadata = '''{"filename": "7c3dda82-a274-40dd-84f1-7ed08b7a917e", "tx_id": "7c3dda82-a274-40dd-84f1-7ed08b7a917e", "survey_id": "lms", "description": "lms survey response for period 2 sample unit ABC123456", "iteration": "2"}'''

dap_desc = '134 survey response for period 201605 sample unit 12346789012A'
survey_desc = '017 survey response for period 201904 sample unit 25462342626B'
feedback_desc = 'lms survey response for period 2 sample unit ABC123456'

dap_iter = '201605'
survey_iter = '201904'
feedback_iter = '2'


class TestDeliver(unittest.TestCase):
    @staticmethod
    def delivery_actual(name, data):
        submission_dict = json.loads(data)
        submission_bytes = json.dumps(submission_dict).encode("utf-8")
        return deliver.deliver(submission_dict, submission_bytes, f'{name}')

    def delivery_bad_response(self, name, data, exception):
        with self.assertRaises(exception) as submission_exception:
            self.delivery_actual(f'{name}', data)
        return str(submission_exception.exception)

    @staticmethod
    def create_metadata_actual(data):
        data_dict = json.loads(data)
        return deliver.create_survey_metadata(data_dict)

    # @mock.patch('app.deliver.post', side_effect=status_code_success)
    def test_deliver_submission_success(self):
        r = requests.Response()
        with mock.patch('app.deliver.post') as mock_post:
            mock_post.return_value = r
            r.status_code = 200
            deliver_dap = self.delivery_actual("dap", dap_data)
            deliver_survey = self.delivery_actual("survey", survey_data)
            deliver_feedback = self.delivery_actual("feedback", feedback_data)
            self.assertTrue(deliver_dap)
            self.assertTrue(deliver_survey)
            self.assertTrue(deliver_feedback)

    def test_deliver_bad_request_response(self):
        bad_response = "Bad Request response from sdx-deliver"
        r = requests.Response()
        with mock.patch('app.deliver.post') as mock_post:
            mock_post.return_value = r
            r.status_code = 400
            dap_exception_str = self.delivery_bad_response('dap', dap_data, QuarantinableError)
            survey_exception_str = self.delivery_bad_response('survey', survey_data, QuarantinableError)
            feedback_exception_str = self.delivery_bad_response('feedback', feedback_data, QuarantinableError)
            self.assertEqual(dap_exception_str, bad_response)
            self.assertEqual(survey_exception_str, bad_response)
            self.assertEqual(feedback_exception_str, bad_response)

    def test_deliver_bad_deliver_response(self):
        bad_response = "Bad response from sdx-deliver"
        r = requests.Response()
        with mock.patch('app.deliver.post') as mock_post:
            mock_post.return_value = r
            r.status_code = 300
            dap_exception_str = self.delivery_bad_response('dap', dap_data, RetryableError)
            survey_exception_str = self.delivery_bad_response('survey', survey_data, RetryableError)
            feedback_exception_str = self.delivery_bad_response('feedback', feedback_data, RetryableError)
            self.assertEqual(dap_exception_str, bad_response)
            self.assertEqual(survey_exception_str, bad_response)
            self.assertEqual(feedback_exception_str, bad_response)

    def test_create_survey_metadata(self):
        dap_test_meta = json.dumps(self.create_metadata_actual(dap_data))
        survey_test_meta = json.dumps(self.create_metadata_actual(survey_data))
        feedback_test_meta = json.dumps(self.create_metadata_actual(feedback_data))
        self.assertEqual(dap_test_meta, dap_metadata)
        self.assertEqual(survey_test_meta, survey_metadata)
        self.assertEqual(feedback_test_meta, feedback_metadata)

    def test_get_desc(self):
        self.assertEqual(dap_desc, deliver.get_description(json.loads(dap_data)))
        self.assertEqual(survey_desc, deliver.get_description(json.loads(survey_data)))
        self.assertEqual(feedback_desc, deliver.get_description(json.loads(feedback_data)))

    def test_get_iter(self):
        self.assertEqual(dap_iter, deliver.get_iteration(json.loads(dap_data)))
        self.assertEqual(survey_iter, deliver.get_iteration(json.loads(survey_data)))
        self.assertEqual(feedback_iter, deliver.get_iteration(json.loads(feedback_data)))

