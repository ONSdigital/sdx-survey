import json
import unittest

from app.definitions.submission import SurveySubmission
from app.response import Response


class TestDV3ToV1Json(unittest.TestCase):
    def setUp(self):
        self.valid_submission: SurveySubmission = {
            "case_id": "fcc58801-6a39-11f1-b510-d594994d468c",
            "tx_id": "fcc58804-6a39-11f1-b510-d594994d468c",
            "type": "uk.gov.ons.edc.eq:surveyresponse",
            "version": "v2",
            "data_version": "0.0.3",
            "origin": "uk.gov.ons.edc.eq",
            "collection_exercise_sid": "fcc58802-6a39-11f1-b510-d594994d468c",
            "flushed": False,
            "submitted_at": "2026-06-17T10:50:59+00:00",
            "launch_language_code": "en",
            "survey_metadata": {
                "survey_id": "147",
                "ru_name": "ESSENTIAL ENTERPRISE LTD.",
                "trad_as": "ESSENTIAL ENTERPRISE LTD.",
                "period_id": "201605",
                "ref_p_start_date": "2022-01-01",
                "ref_p_end_date": "2022-12-31",
                "user_id": "A12345678901",
                "ru_ref": "12346789012A",
                "form_type": "0003"
            },
            "schema_name": "epe_0003",
            "data": {
                "answers": [
                    {
                        "answer_id": "answer8812533d-52fc-4fd1-a32b-0f508245985f",
                        "value": "Yes, I can report for these dates"
                    },
                    {
                        "answer_id": "answer98e0fb74-4dc7-4cf5-9050-b81f094e143a",
                        "value": "Yes"
                    },
                    {
                        "answer_id": "answerd49825a9-3298-438e-9561-78e98472866a",
                        "value": 15000
                    },
                    {
                        "answer_id": "answerc984e2b9-e992-46ca-b19b-9460a84f16ea",
                        "value": 12000
                    },
                ],
                "lists": [],
                "answer_codes": [
                    {
                        "answer_id": "answer8812533d-52fc-4fd1-a32b-0f508245985f",
                        "code": "10"
                    },
                    {
                        "answer_id": "answer98e0fb74-4dc7-4cf5-9050-b81f094e143a",
                        "code": "37"
                    },
                    {
                        "answer_id": "answerd49825a9-3298-438e-9561-78e98472866a",
                        "code": "32"
                    },
                    {
                        "answer_id": "answerc984e2b9-e992-46ca-b19b-9460a84f16ea",
                        "code": "33"
                    },
                ]
            },
            "started_at": "2026-06-17T10:47:56.176770+00:00",
            "submission_language_code": "en"
        }
        self.valid_test_response = Response(self.valid_submission)

        self.invalid_submission: SurveySubmission = {
            "case_id": "fcc58801-6a39-11f1-b510-d594994d468c",
            "tx_id": "fcc58804-6a39-11f1-b510-d594994d468c",
            "type": "uk.gov.ons.edc.eq:surveyresponse",
            "version": "v2",
            "data_version": "0.0.3",
            "origin": "uk.gov.ons.edc.eq",
            "collection_exercise_sid": "fcc58802-6a39-11f1-b510-d594994d468c",
            "flushed": False,
            "submitted_at": "2026-06-17T10:50:59+00:00",
            "launch_language_code": "en",
            "survey_metadata": {
                "survey_id": "147",
                "ru_name": "ESSENTIAL ENTERPRISE LTD.",
                "trad_as": "ESSENTIAL ENTERPRISE LTD.",
                "period_id": "201605",
                "ref_p_start_date": "2022-01-01",
                "ref_p_end_date": "2022-12-31",
                "user_id": "A12345678901",
                "ru_ref": "12346789012A",
                "form_type": "0003"
            },
            "schema_name": "epe_0003",
            "data": {
                "answers": [
                    {
                        "answer_id": "answer8812533d-52fc-4fd1-a32b-0f508245985f",
                        "value": "Yes, I can report for these dates"
                    },
                    {
                        "answer_id": "answer98e0fb74-4dc7-4cf5-9050-b81f094e143a",
                        "value": "Yes"
                    },
                    {
                        "answer_id": "answerd49825a9-3298-438e-9561-78e98472866a",
                        "value": 15000
                    },
                    {
                        "answer_id": "answerc984e2b9-e992-46ca-b19b-9460a84f16ea",
                        "value": 12000
                    },
                    {
                        "answer_id": "answerc984e2b9-e992-46ca-b19b-9460a84f16ea",
                        "value": 4000
                    },
                ],
                "lists": [],
                "answer_codes": [
                    {
                        "answer_id": "answer8812533d-52fc-4fd1-a32b-0f508245985f",
                        "code": "10"
                    },
                    {
                        "answer_id": "answer98e0fb74-4dc7-4cf5-9050-b81f094e143a",
                        "code": "37"
                    },
                    {
                        "answer_id": "answerd49825a9-3298-438e-9561-78e98472866a",
                        "code": "32"
                    },
                    {
                        "answer_id": "answerc984e2b9-e992-46ca-b19b-9460a84f16ea",
                        "code": "33"
                    },
                ]
            },
            "started_at": "2026-06-17T10:47:56.176770+00:00",
            "submission_language_code": "en"
        }
        self.invalid_test_response = Response(self.invalid_submission)

    def test_valid_epe_get_file_contents(self):
        expected = {
            "case_id": "fcc58801-6a39-11f1-b510-d594994d468c",
            "tx_id": "fcc58804-6a39-11f1-b510-d594994d468c",
            "type": "uk.gov.ons.edc.eq:surveyresponse",
            "version": "0.0.1",
            "origin": "uk.gov.ons.edc.eq",
            "survey_id": "147",
            "flushed": False,
            "submitted_at": "2026-06-17T10:50:59+00:00",
            "collection": {
                "exercise_sid": "fcc58802-6a39-11f1-b510-d594994d468c",
                "schema_name": "epe_0003",
                "period": "201605",
                "instrument_id": "0003",
            },
            "metadata": {
                "user_id": "A12345678901",
                "ru_ref": "12346789012A",
                "ref_period_start_date": "2022-01-01",
                "ref_period_end_date": "2022-12-31",
            },
            "launch_language_code": "en",
            "data": {
                "10": "Yes, I can report for these dates",
                "37": "Yes",
                "32": "15000",
                "33": "12000",
            },
            "form_type": "0003",
            "started_at": "2026-06-17T10:47:56.176770+00:00",
            "submission_language_code": "en",
        }

        actual = self.valid_test_response.to_v1_json()
        self.maxDiff = None
        self.assertEqual(expected, json.loads(actual))

    def test_invalid_epe_get_file_contents_returns_v3_data(self):
        expected = {
            'case_id': 'fcc58801-6a39-11f1-b510-d594994d468c',
            'collection': {
                'exercise_sid': 'fcc58802-6a39-11f1-b510-d594994d468c',
                'instrument_id': '0003',
                'period': '201605',
                'schema_name': 'epe_0003'
            },
            'data': {
                'answer_codes':
                    [
                        {
                            'answer_id': 'answer8812533d-52fc-4fd1-a32b-0f508245985f',
                            'code': '10'
                        },
                        {
                            'answer_id': 'answer98e0fb74-4dc7-4cf5-9050-b81f094e143a',
                            'code': '37'
                        },
                        {
                            'answer_id': 'answerd49825a9-3298-438e-9561-78e98472866a',
                            'code': '32'
                        },
                        {
                            'answer_id': 'answerc984e2b9-e992-46ca-b19b-9460a84f16ea',
                            'code': '33'
                        }
                    ],
                'answers': [
                    {
                        'answer_id': 'answer8812533d-52fc-4fd1-a32b-0f508245985f',
                        'value': 'Yes, I can report for these dates'
                    },
                    {
                        'answer_id': 'answer98e0fb74-4dc7-4cf5-9050-b81f094e143a',
                        'value': 'Yes'
                    },
                    {
                        'answer_id': 'answerd49825a9-3298-438e-9561-78e98472866a',
                        'value': 15000
                    },
                    {
                        'answer_id': 'answerc984e2b9-e992-46ca-b19b-9460a84f16ea',
                        'value': 12000
                    },
                    {
                        'answer_id': 'answerc984e2b9-e992-46ca-b19b-9460a84f16ea',
                        'value': 4000
                    }
                ],
                'lists': []},
            'flushed': False,
            'form_type': '0003',
            'launch_language_code': 'en',
            'metadata': {'ref_period_end_date': '2022-12-31',
                         'ref_period_start_date': '2022-01-01',
                         'ru_ref': '12346789012A',
                         'user_id': 'A12345678901'},
            'origin': 'uk.gov.ons.edc.eq',
            'started_at': '2026-06-17T10:47:56.176770+00:00',
            'submission_language_code': 'en',
            'submitted_at': '2026-06-17T10:50:59+00:00',
            'survey_id': '147',
            'tx_id': 'fcc58804-6a39-11f1-b510-d594994d468c',
            'type': 'uk.gov.ons.edc.eq:surveyresponse',
            'version': '0.0.3'
        }
        
        actual = self.invalid_test_response.to_v1_json()
        self.maxDiff = None
        self.assertEqual(expected, json.loads(actual))
