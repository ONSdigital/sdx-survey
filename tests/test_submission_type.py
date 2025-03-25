import unittest
from unittest.mock import patch, Mock

from sdx_gcp.errors import DataError

from app import submission_type
from app.definitions.submission import SurveySubmission
from app.response import get_safe_submission, SurveyType, ResponseType, SchemaVersion, Response
from tests import get_response, get_json


class TestGetResponseType(unittest.TestCase):

    def test_survey_legacy(self):
        self.assertEqual(ResponseType.SURVEY, get_response("submission").get_response_type())

    def test_feedback_legacy(self):
        self.assertEqual(ResponseType.FEEDBACK, get_response("feedback").get_response_type())

    def test_survey_v1(self):
        self.assertEqual(ResponseType.SURVEY, get_response("survey_v1_001").get_response_type())

    def test_survey_v2(self):
        self.assertEqual(ResponseType.SURVEY, get_response("survey_v2_001").get_response_type())

    def test_survey_adhoc(self):
        self.assertEqual(ResponseType.SURVEY, get_response("survey_adhoc_001").get_response_type())

    def test_feedback_v1(self):
        self.assertEqual(ResponseType.FEEDBACK, get_response("feedback_v1_001").get_response_type())

    def test_feedback_v2(self):
        self.assertEqual(ResponseType.FEEDBACK, get_response("feedback_v2_001").get_response_type())

    def test_feedback_adhoc(self):
        self.assertEqual(ResponseType.FEEDBACK, get_response("feedback_adhoc_001").get_response_type())


class TestGetSurveyType(unittest.TestCase):

    def test_survey_legacy(self):
        self.assertEqual(SurveyType.BUSINESS, get_response("submission").get_survey_type())

    def test_feedback_legacy(self):
        self.assertEqual(SurveyType.BUSINESS, get_response("feedback").get_survey_type())

    def test_survey_v1(self):
        self.assertEqual(SurveyType.BUSINESS, get_response("survey_v1_001").get_survey_type())

    def test_survey_v2(self):
        self.assertEqual(SurveyType.BUSINESS, get_response("survey_v2_001").get_survey_type())

    def test_survey_adhoc(self):
        self.assertEqual(SurveyType.ADHOC, get_response("survey_adhoc_001").get_survey_type())

    def test_feedback_v1(self):
        self.assertEqual(SurveyType.BUSINESS, get_response("feedback_v1_001").get_survey_type())

    def test_feedback_v2(self):
        self.assertEqual(SurveyType.BUSINESS, get_response("feedback_v2_001").get_survey_type())

    def test_feedback_adhoc(self):
        self.assertEqual(SurveyType.ADHOC, get_response("feedback_adhoc_001").get_survey_type())


class TestGetFormType(unittest.TestCase):

    def test_get_form_type_feedback_v2(self):
        self.assertEqual("0253", get_response("feedback_v2_001").get_form_type())


class TestGetPeriodDates(unittest.TestCase):

    def test_get_v2_period_start_date(self):
        self.assertEqual("2021-01-01", get_response("survey_v2_001").get_period_start_date())

    def test_get_v1_period_start_date(self):
        self.assertEqual("2019-07-01", get_response("survey_v1_001").get_period_start_date())

    def test_get_v2_period_end_date(self):
        self.assertEqual("2021-06-01", get_response("survey_v2_001").get_period_end_date())

    def test_get_v1_period_end_date(self):
        self.assertEqual("2019-10-31", get_response("survey_v1_001").get_period_end_date())


class TestGetSchemaVersion(unittest.TestCase):

    def test_survey_legacy(self):
        self.assertEqual(SchemaVersion.V1, get_response("submission").get_schema_version())

    def test_feedback_legacy(self):
        self.assertEqual(SchemaVersion.V1, get_response("feedback").get_schema_version())

    def test_survey_v1(self):
        self.assertEqual(SchemaVersion.V1, get_response("survey_v1_001").get_schema_version())

    def test_survey_v2(self):
        self.assertEqual(SchemaVersion.V2, get_response("survey_v2_001").get_schema_version())

    def test_survey_adhoc(self):
        self.assertEqual(SchemaVersion.V2, get_response("survey_adhoc_001").get_schema_version())

    def test_feedback_v1(self):
        self.assertEqual(SchemaVersion.V1, get_response("feedback_v1_001").get_schema_version())

    def test_feedback_v2(self):
        self.assertEqual(SchemaVersion.V2, get_response("feedback_v2_001").get_schema_version())

    def test_feedback_adhoc(self):
        self.assertEqual(SchemaVersion.V2, get_response("feedback_adhoc_001").get_schema_version())


class TestSppSubmission(unittest.TestCase):

    def setUp(self):
        self.fake_survey_id: str = "123"
        self.fake_period_id: str = "2504"
        mock_spp_mapping = {
            self.fake_survey_id: self.fake_period_id
        }
        submission_type._SPP_SURVEYS = mock_spp_mapping

    @patch("app.submission_type.v2_nifi_message_submission")
    def test_spp_submission_true(self, mock_v2: Mock):
        mock_v2.return_value = True
        response_json: SurveySubmission = get_json("survey_v2_001")
        response_json["survey_metadata"]["survey_id"] = self.fake_survey_id
        response_json["survey_metadata"]["period_id"] = self.fake_period_id

        actual = submission_type.spp_submission(Response(response_json, "ea82c224-0f80-41cc-b877-8a7804b56c26"))
        self.assertTrue(actual)

    @patch("app.submission_type.v2_nifi_message_submission")
    def test_spp_submission_false(self, mock_v2: Mock):
        wrong_survey_id: str = "456"
        mock_v2.return_value = True
        response_json: SurveySubmission = get_json("survey_v2_001")
        response_json["survey_metadata"]["survey_id"] = wrong_survey_id
        response_json["survey_metadata"]["period_id"] = self.fake_period_id

        actual = submission_type.spp_submission(Response(response_json, "ea82c224-0f80-41cc-b877-8a7804b56c26"))
        self.assertFalse(actual)

    @patch("app.submission_type.v2_nifi_message_submission")
    def test_spp_submission_false_prior_period(self, mock_v2: Mock):
        earlier_period: str = "2503"
        mock_v2.return_value = True
        response_json: SurveySubmission = get_json("survey_v2_001")
        response_json["survey_metadata"]["survey_id"] = self.fake_survey_id
        response_json["survey_metadata"]["period_id"] = earlier_period

        actual = submission_type.spp_submission(Response(response_json, "ea82c224-0f80-41cc-b877-8a7804b56c26"))
        self.assertFalse(actual)


class TestMissing(unittest.TestCase):

    def test_survey_v1_missing_survey_id(self):
        data: Response = get_response("survey_v1_001")
        data._submission.pop('survey_id')
        with self.assertRaises(DataError):
            data.get_survey_id()

    def test_survey_v2_missing_survey_id(self):
        data = get_response("survey_v2_001")
        data._submission["survey_metadata"].pop("survey_id")
        with self.assertRaises(DataError):
            data.get_survey_id()


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
