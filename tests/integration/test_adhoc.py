from typing import Self

from app.definitions.context import Context
from app.definitions.context_type import ContextType
from app.definitions.survey_type import SurveyType
from tests.integration.test_base import TestBase


class TestAdhoc(TestBase):
    def test_phm(self: Self):
        self.set_survey_submission("740.0001.json")

        resp = self.client.post("/", json=self.envelope)

        expected_filename = "cebf9e22-0b78-40d8-872d-ca5fe2507ab1.json"

        actual_files = self.get_zip_contents()

        expected_context: Context = {
            "tx_id": "cebf9e22-0b78-40d8-872d-ca5fe2507ab1",
            "survey_type": SurveyType.ADHOC,
            "context_type": ContextType.ADHOC_SURVEY,
            "survey_id": "740",
        }

        expected_receipt = {"data": {"qid": "0130000001408548"}}

        self.assertTrue(resp.is_success)
        self.assertTrue(expected_filename in actual_files)
        self.assertEqual(1, len(actual_files))
        self.assertEqual(expected_context, self.get_context())
        self.assertEqual(expected_receipt, self.get_receipt())
        # check comments were not stored
        self.mock_datastore.commit_entity.assert_not_called()
