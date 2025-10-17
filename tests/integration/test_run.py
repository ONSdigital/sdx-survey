from tests.integration.test_base import TestBase, get_json


class TestRun(TestBase):
    def test_run_success(self):
        submission_json = get_json("009.0106.json")
        tx_id = submission_json["tx_id"]
        self.set_survey_submission(tx_id, submission_json)

        resp = self.client.post("/", json=self.envelope)

        self.assertTrue(resp.is_success)

    def test_bad_data_is_acked(self):
        # We want it to be acked so that it is not sent again from pubsub
        submission_json = get_json("009.0106.json")
        tx_id = submission_json["tx_id"]
        submission_json["survey_metadata"]["survey_id"] = "999"
        self.set_survey_submission(tx_id, submission_json)

        resp = self.client.post("/", json=self.envelope)

        self.assertTrue(resp.is_success)

    def test_retryable_error_is_nacked(self):
        # We want it to be nacked so that it will be sent again from pubsub
        submission_json = get_json("009.0106.json")
        tx_id = submission_json["tx_id"]
        self.set_survey_submission(tx_id, submission_json)
        self.simulate_retryable_error_on_post()

        resp = self.client.post("/", json=self.envelope)

        self.assertFalse(resp.is_success)

    def test_data_error_from_post_is_nacked(self):
        # Simulate a 400 being returned from another microservice
        # We want it to be acked so that it is not sent again from pubsub
        submission_json = get_json("009.0106.json")
        tx_id = submission_json["tx_id"]
        self.set_survey_submission(tx_id, submission_json)
        self.simulate_data_error_on_post()

        resp = self.client.post("/", json=self.envelope)

        self.assertTrue(resp.is_success)
