import unittest

from app.definitions.submission import SurveySubmission
from app.response import Response
from app.transformation.transforms import image


class TestImage(unittest.TestCase):

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
                "survey_id": "202",
                "user_id": "UNKNOWN",
                "ru_ref": "12346789012A",
                "ru_name": "ESSENTIAL ENTERPRISE LTD.",
                "trad_as": "ESSENTIAL ENTERPRISE LTD.",
                "period_id": "201605",
                "ref_p_start_date": "2016-05-01",
                "ref_p_end_date": "2016-05-31",
                "form_type": "1801"
            },
            "data": {'001': 'hi'},
            "started_at": "2023-09-29T09:07:10.640686+00:00",
            "submission_language_code": "en"
        }

    def test_get_name(self):
        actual: str = image.get_name(Response(self.submission))
        expected = "Sbefa5444749f407a_1.JPG"
        self.assertEqual(expected, actual)
