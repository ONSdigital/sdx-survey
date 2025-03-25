import datetime
import unittest
from unittest.mock import patch

from app.definitions.submission import SurveySubmission
from app.response import Response
from app.transform.transforms import index


class TestIndex(unittest.TestCase):

    def setUp(self):
        self.tx_id = "befa5444-749f-407a-b3a2-19f1d1c7324b"
        self.submission = {
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

    @patch('app.transform.transforms.index.datetime')
    def test_index_contents(self, mock_datetime):

        mock_datetime.datetime.utcnow.return_value = datetime.datetime.strptime("2023-11-03", "%Y-%m-%d")
        image_name = "Sbefa5444749f407ab3a219f1d1c7324b_1.JPG"
        actual: bytes = index.get_contents(Response(self.submission, self.tx_id), image_name)
        expected = (b'03/11/2023 00:00:00,\\EDC_QImages\\Images\\Sbefa5444749f407ab3a219f1d1c7324b_1.JPG,20231103,'
                    b'Sbefa5444749f407ab3a219f1d1c7324b_1,202,1801,12346789012,201605,001,0')
        self.assertEqual(expected, actual)

    @patch('app.transform.transforms.index.datetime')
    def test_index_contents_4_digit_period(self, mock_datetime):
        mock_datetime.datetime.utcnow.return_value = datetime.datetime.strptime("2023-11-03", "%Y-%m-%d")
        image_name = "Sbefa5444749f407ab3a219f1d1c7324b_1.JPG"
        submission: SurveySubmission = self.submission
        submission["survey_metadata"]["period_id"] = "2310"
        actual: bytes = index.get_contents(Response(self.submission, self.tx_id), image_name)
        expected = (b'03/11/2023 00:00:00,\\EDC_QImages\\Images\\Sbefa5444749f407ab3a219f1d1c7324b_1.JPG,20231103,'
                    b'Sbefa5444749f407ab3a219f1d1c7324b_1,202,1801,12346789012,202310,001,0')
        self.assertEqual(expected, actual)

    def test_index_name(self):
        actual: str = index.get_name(Response(self.submission, self.tx_id))
        expected = "EDC_202_20230929_befa5444749f407a.csv"
        self.assertEqual(expected, actual)
