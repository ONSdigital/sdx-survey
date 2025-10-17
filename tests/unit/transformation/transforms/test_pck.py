import unittest

from app.definitions.submission import SurveySubmission
from app.response import Response
from app.transformation.transforms import pck


class TestPCK(unittest.TestCase):

    def setUp(self):
        self.submission: SurveySubmission = {
            "case_id": "34d30023-ee05-4f7c-b5a5-12639b4f045e",
            "tx_id": "befa5444-749f-407a-b3a2-19f1d1c7324b",
            "type": "uk.gov.ons.edc.eq:surveyresponse",
            "version": "v2",
            "data_version": "0.0.1",
            "origin": "uk.gov.ons.edc.eq",
            "collection_exercise_sid": "e666daad-cdda-4dac-812f-fa9b9361258f",
            "schema_name": "test_1801",
            "flushed": False,
            "submitted_at": "2023-09-29T09:30:21+00:00",
            "launch_language_code": "en",
            "survey_metadata": {
                "survey_id": "144",
                "user_id": "UNKNOWN",
                "ru_ref": "12346789012A",
                "ru_name": "ESSENTIAL ENTERPRISE LTD.",
                "trad_as": "ESSENTIAL ENTERPRISE LTD.",
                "period_id": "201605",
                "ref_p_start_date": "2016-05-01",
                "ref_p_end_date": "2016-05-31",
                "form_type": "0001"
            },
            "data": {'001': 'hi'},
            "started_at": "2023-09-29T09:07:10.640686+00:00",
            "submission_language_code": "en"
        }

    def test_get_name(self):
        actual: str = pck.get_name(Response(self.submission))
        expected = "144_befa5444749f407a"
        self.assertEqual(expected, actual)

    def test_get_abs_name(self):
        submission: SurveySubmission = self.submission
        submission["survey_metadata"]["survey_id"] = "202"
        submission["survey_metadata"]["form_type"] = "1802"

        actual = pck.get_name(Response(submission))
        expected = "053_befa5444749f407a"
        self.assertEqual(expected, actual)
