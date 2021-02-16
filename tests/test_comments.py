import json
import unittest
from unittest.mock import patch

from app.comments import store_comments, get_comment, get_additional_comments, get_boxes_selected


class TestGetComments(unittest.TestCase):

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
