import unittest
from unittest.mock import patch

from requests import Session, exceptions
from urllib3.exceptions import MaxRetryError

from app.deliver import deliver_feedback, deliver_survey, deliver_dap, deliver, post, DAP, deliver_hybrid
from app.errors import QuarantinableError, RetryableError


class TestCollect(unittest.TestCase):
    test_survey = {
        "case_id": "bb9eaf11-a729-40b5-8d17-d112e018c0d5",
        "collection": {
            "exercise_sid": "664dbdf4-02fb-4d68-b0cf-7f7402df00e5",
            "instrument_id": "0011",
            "period": "201904"
        },
        "data": {
            "15": "No",
            "119": "150",
            "120": "152",
            "144": "200",
            "145": "124",
            "146": "This is a comment"
        },
        "flushed": False,
        "metadata": {
            "ref_period_end_date": "2018-11-29",
            "ref_period_start_date": "2019-04-01",
            "ru_ref": "15162882666F",
            "user_id": "UNKNOWN"
        },
        "origin": "uk.gov.ons.edc.eq",
        "started_at": "2019-04-01T14:00:24.224709",
        "submitted_at": "2019-04-01T14:10:26.933601",
        "survey_id": "017",
        "tx_id": "1027a13a-c253-4e9d-9e78-d0f0cfdd3988",
        "type": "uk.gov.ons.edc.eq:surveyresponse",
        "version": "0.0.1"
    }

    test_bytes = b'bytes'

    @patch.object(Session, 'post')
    def test_post_feedback_200(self, mock_post):
        mock_post.return_value.status_code = 200
        deliver_feedback(self.test_survey, filename="1027a13a-c253-4e9d-9e78-d0f0cfdd3988")
        mock_post.assert_called()

    @patch.object(Session, 'post')
    def test_post_survey_200(self, mock_post):
        mock_post.return_value.status_code = 200
        deliver_survey(self.test_survey, self.test_bytes)
        mock_post.assert_called()

    @patch.object(Session, 'post')
    def test_post_hybrid_200(self, mock_post):
        mock_post.return_value.status_code = 200
        deliver_hybrid(self.test_survey, self.test_bytes)
        mock_post.assert_called()

    @patch.object(Session, 'post')
    def test_post_dap_200(self, mock_post):
        mock_post.return_value.status_code = 200
        deliver_dap(self.test_survey)
        mock_post.assert_called()

    @patch.object(Session, 'post')
    def test_400_response(self, mock_post):
        with self.assertRaises(QuarantinableError):
            mock_post.return_value.status_code = 400
            assert deliver(self.test_survey, 'feedback')
            mock_post.assert_called()

    @patch.object(Session, 'post')
    def test_300_response(self, mock_post):
        with self.assertRaises(RetryableError):
            mock_post.return_value.status_code = 300
            assert deliver(self.test_survey, 'feedback')
            mock_post.assert_called()

    @patch('app.deliver.session')
    def test_post_MaxRetryError(self, mock_session):
        mock_session.post.side_effect = MaxRetryError("pool", "url", "reason")
        with self.assertRaises(RetryableError):
            post("filename", {}, DAP)

    @patch('app.deliver.session')
    def test_post_ConnectionError(self, mock_session):
        mock_session.post.side_effect = exceptions.ConnectionError()
        with self.assertRaises(RetryableError):
            post("filename", {}, DAP)
