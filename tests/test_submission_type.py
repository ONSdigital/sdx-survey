import unittest

from sdx_gcp.errors import DataError

from app.submission_type import get_response_type, ResponseType, get_survey_type, SurveyType, get_schema_version, \
    SchemaVersion, get_survey_id, get_form_type, get_period_start_date, get_period_end_date, get_safe_submission
from tests import get_data


class TestGetResponseType(unittest.TestCase):

    def test_survey_legacy(self):
        self.assertEqual(ResponseType.SURVEY, get_response_type(get_data("submission")))

    def test_feedback_legacy(self):
        self.assertEqual(ResponseType.FEEDBACK, get_response_type(get_data("feedback")))

    def test_survey_v1(self):
        self.assertEqual(ResponseType.SURVEY, get_response_type(get_data("survey_v1_001")))

    def test_survey_v2(self):
        self.assertEqual(ResponseType.SURVEY, get_response_type(get_data("survey_v2_001")))

    def test_survey_adhoc(self):
        self.assertEqual(ResponseType.SURVEY, get_response_type(get_data("survey_adhoc_001")))

    def test_feedback_v1(self):
        self.assertEqual(ResponseType.FEEDBACK, get_response_type(get_data("feedback_v1_001")))

    def test_feedback_v2(self):
        self.assertEqual(ResponseType.FEEDBACK, get_response_type(get_data("feedback_v2_001")))

    def test_feedback_adhoc(self):
        self.assertEqual(ResponseType.FEEDBACK, get_response_type(get_data("feedback_adhoc_001")))


class TestGetSurveyType(unittest.TestCase):

    def test_survey_legacy(self):
        self.assertEqual(SurveyType.BUSINESS, get_survey_type(get_data("submission")))

    def test_feedback_legacy(self):
        self.assertEqual(SurveyType.BUSINESS, get_survey_type(get_data("feedback")))

    def test_survey_v1(self):
        self.assertEqual(SurveyType.BUSINESS, get_survey_type(get_data("survey_v1_001")))

    def test_survey_v2(self):
        self.assertEqual(SurveyType.BUSINESS, get_survey_type(get_data("survey_v2_001")))

    def test_survey_adhoc(self):
        self.assertEqual(SurveyType.ADHOC, get_survey_type(get_data("survey_adhoc_001")))

    def test_feedback_v1(self):
        self.assertEqual(SurveyType.BUSINESS, get_survey_type(get_data("feedback_v1_001")))

    def test_feedback_v2(self):
        self.assertEqual(SurveyType.BUSINESS, get_survey_type(get_data("feedback_v2_001")))

    def test_feedback_adhoc(self):
        self.assertEqual(SurveyType.ADHOC, get_survey_type(get_data("feedback_adhoc_001")))


class TestGetFormType(unittest.TestCase):

    def test_get_form_type_feedback_v2(self):
        self.assertEqual("0253", get_form_type(get_data("feedback_v2_001")))


class TestGetPeriodDates(unittest.TestCase):

    def test_get_v2_period_start_date(self):
        self.assertEqual("2021-01-01", get_period_start_date(get_data("survey_v2_001")))

    def test_get_v1_period_start_date(self):
        self.assertEqual("2019-07-01", get_period_start_date(get_data("survey_v1_001")))

    def test_get_v2_period_end_date(self):
        self.assertEqual("2021-06-01", get_period_end_date(get_data("survey_v2_001")))

    def test_get_v1_period_end_date(self):
        self.assertEqual("2019-10-31", get_period_end_date(get_data("survey_v1_001")))


class TestGetSchemaVersion(unittest.TestCase):

    def test_survey_legacy(self):
        self.assertEqual(SchemaVersion.V1, get_schema_version(get_data("submission")))

    def test_feedback_legacy(self):
        self.assertEqual(SchemaVersion.V1, get_schema_version(get_data("feedback")))

    def test_survey_v1(self):
        self.assertEqual(SchemaVersion.V1, get_schema_version(get_data("survey_v1_001")))

    def test_survey_v2(self):
        self.assertEqual(SchemaVersion.V2, get_schema_version(get_data("survey_v2_001")))

    def test_survey_adhoc(self):
        self.assertEqual(SchemaVersion.V2, get_schema_version(get_data("survey_adhoc_001")))

    def test_feedback_v1(self):
        self.assertEqual(SchemaVersion.V1, get_schema_version(get_data("feedback_v1_001")))

    def test_feedback_v2(self):
        self.assertEqual(SchemaVersion.V2, get_schema_version(get_data("feedback_v2_001")))

    def test_feedback_adhoc(self):
        self.assertEqual(SchemaVersion.V2, get_schema_version(get_data("feedback_adhoc_001")))


class TestMissing(unittest.TestCase):

    def test_survey_v1_missing_survey_id(self):
        data = get_data("survey_v1_001")
        data.pop("survey_id")
        with self.assertRaises(DataError):
            get_survey_id(data)

    def test_survey_v2_missing_survey_id(self):
        data = get_data("survey_v2_001")
        data["survey_metadata"].pop("survey_id")
        with self.assertRaises(DataError):
            get_survey_id(data)


class TestGetSafeSubmission(unittest.TestCase):

    def test_makes_submission_safe(self):

        my_dict = {
            "tx_id": "super_secret_thing",
            "data": {
                "q1": "answer1",
                "q2": "answer2",
                "more": ["answer3", "answer4"]
            },
            "date": "d1"
        }

        expected = {
            "tx_id": "",
            "data": {
                "q1": "",
                "q2": "",
                "more": ["", ""]
            },
            "date": ""
        }

        self.assertEqual(get_safe_submission(my_dict), expected)
