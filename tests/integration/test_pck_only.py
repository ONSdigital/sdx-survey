from typing import Self

from app.definitions.context import Context
from app.definitions.context_type import ContextType
from app.definitions.survey_type import SurveyType
from tests.integration.test_base import TestBase


class TestPckOnly(TestBase):
    def test_ashe(self: Self):
        self.set_survey_submission("141.0001.json")

        resp = self.client.post("/", json=self.envelope)

        expected_pck_filename = "141_bddbb41275ea43ce"

        actual_files = self.get_zip_contents()

        expected_context: Context = {
            "tx_id": "bddbb412-75ea-43ce-9efa-0deb07cb8550",
            "survey_type": SurveyType.DEXTA,
            "context_type": ContextType.BUSINESS_SURVEY,
            "survey_id": "141",
            "period_id": "1605",
            "ru_ref": "12346789012A",
        }

        self.assertTrue(resp.is_success)
        self.assertEqual(self.pck_contents, actual_files[expected_pck_filename])
        self.assertEqual(1, len(actual_files))
        self.assertEqual(expected_context, self.get_context())
