import unittest

from app.submission_type import get_response_type, ResponseType, get_survey_type, SurveyType, get_schema_version, \
    SchemaVersion
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
