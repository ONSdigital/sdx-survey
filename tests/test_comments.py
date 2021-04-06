import json
import unittest
from unittest import mock

import pytest
from google.cloud import datastore
from unittest.mock import patch
from cryptography.fernet import Fernet
from app import CONFIG
from app.comments import get_comment, get_additional_comments, get_boxes_selected, encrypt_comment, store_comments
from app.errors import QuarantinableError


class TestGetComments(unittest.TestCase):
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

    @patch('app.comments.extract_comment')
    def test_get_comment_187(self, extract_comment):
        test_data = {
            'tx_id': '0f534ffc-9442-414c-b39f-a756b4adc6cb',
            'survey_id': '187',
            'type': 'uk.gov.ons.edc.eq:feedback'
        }
        get_comment(test_data)
        extract_comment.assert_called_with(test_data, "500")

    def test_get_comment(self):
        test_data = {
            'data': {
                "500": "Im the 500 comment",
                "300": "Im the 300 comment",
                "146": "Im the 146 comment",
            },
            'tx_id': '0f534ffc-9442-414c-b39f-a756b4adc6cb',
            'survey_id': '187',
            'type': 'uk.gov.ons.edc.eq:feedback'
        }
        self.assertEqual(get_comment(test_data), 'Im the 500 comment')
        test_data['survey_id'] = '134'
        self.assertEqual(get_comment(test_data), 'Im the 300 comment')
        test_data['survey_id'] = '017'
        self.assertEqual(get_comment(test_data), 'Im the 146 comment')

    def test_get_additional_comments(self):
        test_data = {
            'data': {
                "300w": "300w",
                "300m": "300m",
                "300w5": "300w5"
            },
            'tx_id': '0f534ffc-9442-414c-b39f-a756b4adc6cb',
            'survey_id': '134',
            'type': 'uk.gov.ons.edc.eq:feedback'
        }
        self.assertEqual(get_additional_comments(test_data), [{'qcode': '300w', "comment": '300w'},
                                                              {'qcode': '300m', "comment": '300m'},
                                                              {'qcode': '300w5', "comment": '300w5'}])

    def test_get_additional_comments_none(self):
        test_data = {
            'data': {
                "300a": "300w",
                "300b": "300m",
                "300c": "300w5"
            },
            'tx_id': '0f534ffc-9442-414c-b39f-a756b4adc6cb',
            'survey_id': '134',
            'type': 'uk.gov.ons.edc.eq:feedback'
        }
        self.assertEqual(get_additional_comments(test_data), [])

    def test_get_boxes_selected(self):
        test_data = {
            'data': {
                "91w": "Yes",
                "94w2": "Yes",
                "192w42": "Yes",
                "197w4": "Yes"
            },
            'tx_id': '0f534ffc-9442-414c-b39f-a756b4adc6cb',
            'survey_id': '134',
            'type': 'uk.gov.ons.edc.eq:feedback'
        }
        self.assertEqual(get_boxes_selected(test_data), "91w, 94w2, 192w42, 197w4, ")

    def test_get_boxes_selected_none(self):
        test_data = {
            'data': {
                "91w123": "Yes",
                "94w2123": "Yes",
                "192w42123": "Yes",
                "197w4123": "Yes"
            },
            'tx_id': '0f534ffc-9442-414c-b39f-a756b4adc6cb',
            'survey_id': '134',
            'type': 'uk.gov.ons.edc.eq:feedback'
        }
        self.assertEqual(get_boxes_selected(test_data), "")

    def test_encryption_comments(self):
        test_data = {'additional': [{'comment': 'Pipe mania', 'qcode': '300w'},
                                    {'comment': 'Gas leak', 'qcode': '300f'},
                                    {'comment': 'copper pipe', 'qcode': '300m'},
                                    {'comment': 'solder joint', 'qcode': '300w4'},
                                    {'comment': 'drill hole', 'qcode': '300w5'}],
                     'boxes_selected': '91w, 95w, 96w, 97w, 91f, 95f, 96f, 97f, 191m, 195m, 196m, '
                                       '197m, 191w4, 195w4, 196w4, 197w4, 191w5, 195w5, 196w5, '
                                       '197w5, ',
                     'comment': 'flux clean',
                     'ru_ref': '12346789012A'
                     }
        encrypted_data = encrypt_comment(test_data)
        self.assertEqual(decrypt_comment(encrypted_data), test_data)

    @mock.patch('app.comments.commit_to_datastore')
    def test_store_comments_valid(self, mock_datastore):
        store_comments(self.test_survey)
        mock_datastore.assert_called()


def decrypt_comment(comment_token: str) -> dict:
    f = Fernet(CONFIG.ENCRYPT_COMMENT_KEY)
    comment_bytes = f.decrypt(comment_token.encode())
    return json.loads(comment_bytes.decode())
