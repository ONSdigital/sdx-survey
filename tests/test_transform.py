import unittest
import os
import json
from unittest.mock import patch

import pytest
import requests
from zipfile import ZipFile
from unittest import mock

from urllib3.exceptions import MaxRetryError
from requests.exceptions import ConnectionError
from app.errors import QuarantinableError, RetryableError
from requests import Session
from app import transform
from app.transform import post, V1


class ResponseContent:
    def __init__(self, number):
        with open('sample_file.txt', 'w') as file:
            file.write('This is some dummy text')
            file.close()
        zip_file = ZipFile('sample.zip', 'w')
        zip_file.write('sample_file.txt')
        zip_file.close()
        self.content = zip_file


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


def remove_file(file):
    if os.path.exists(file):
        os.remove(file)
    else:
        pass


class TestTransform(unittest.TestCase):

    def test_deliver_submission_success(self):
        r = requests.Response()
        with mock.patch('app.transform.post') as mock_post:
            mock_post.return_value = r
            r.status_code = 200
            with mock.patch('requests.models.Response.content') as mock_content:
                mock_content.return_value = ResponseContent
                dap_dict = json.loads(dap_data)
                transform_dap = transform.transform(dap_dict)
                self.assertTrue(transform_dap)
        remove_file('sample_file.txt')
        remove_file('sample.zip')

    def test_transform_bad_response(self):
        bad_response = "Bad response from sdx-transform"
        r = requests.Response()
        with mock.patch('app.transform.post') as mock_post:
            mock_post.return_value = r
            r.status_code = 300
            with mock.patch('requests.models.Response.content') as mock_content:
                mock_content.return_value = ResponseContent
                dap_dict = json.loads(dap_data)
                with self.assertRaises(QuarantinableError) as submission_exception:
                    transform.transform(dap_dict)
                self.assertEqual(str(submission_exception.exception), bad_response)

    def test_transform_bad_request_response(self):
        bad_response = "Bad response from sdx-transform"
        r = requests.Response()
        with mock.patch('app.transform.post') as mock_post:
            mock_post.return_value = r
            r.status_code = 400
            with mock.patch('requests.models.Response.content') as mock_content:
                mock_content.return_value = ResponseContent
                dap_dict = json.loads(dap_data)
                with self.assertRaises(QuarantinableError) as submission_exception:
                    transform.transform(dap_dict)
                self.assertEqual(str(submission_exception.exception), bad_response)

    @patch.object(Session, 'post')
    def test_post(self, mock_request):
        with pytest.raises(QuarantinableError):
            mock_request.return_value.status_code = 400
            transform.transform(dap_data, V1)

    @patch('app.transform.session')
    def test_post_MaxRetryError(self, mock_session):
        survey_json = '{"tx_id":"123"}'
        mock_session.post.side_effect = MaxRetryError("pool", "url", "reason")
        with pytest.raises(RetryableError):
            post(survey_json, V1)

    @patch('app.transform.session')
    def test_post_ConnectionError(self, mock_session):
        survey_json = '{"tx_id":"123"}'
        mock_session.post.side_effect = ConnectionError()
        with pytest.raises(RetryableError):
            post(survey_json, V1)
