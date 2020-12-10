import json
import unittest
from app import publish_dap


class DapPublisherTest(unittest.TestCase):

    def test_create_dap_message(self):
        data = '''{
"case_id": "846b8188-8235-4025-a5ef-5b98c693d6f1",
"collection": {
"exercise_sid": "cfee310c-082f-4c09-99af-46e14fb9ec71",
"instrument_id": "0001",
"period": "201605"
},
"data": {
"1": "Yes",
"10": "Yes",
"11": "Importing comment",
"12": "It will get harder",
"13": "Yes, but we have had to change suppliers or find alternative solutions",
"146": "Anything else comment",
"15": "Some prices increased, some prices decreased",
"16": "Prices changing comment",
"17": "Expect prices to generally increase",
"18": "Yes, we generally had to increase our prices",
"19": "Prices changing comment",
"2": "No, it was outside the normal range",
"20": "Not sure",
"21": "Yes, access to finance has increased",
"22": "Don't know yet",
"23": "Yes, the workforce could meet the business's demands",
"241": "Increased working hours",
"243": "Staff are encouraged to work from home",
"246": "Recruiting staff for the short term",
"251": "40",
"252": "30",
"253": "10",
"254": "5",
"255": "5",
"256": "10",
"26": "Expect workforce size to increase",
"27": "Yes",
"28": "Financial or operational activities comment",
"29": "Yes, I expect other financial and/or operational activities to be affected",
"3": "Turnover was lower than normal",
"30": "Finance and operations in the next 2 weeks comment",
"41": "Coronavirus (COVID-19) outbreak",
"42": "Other turnover reason over 2 weeks",
"5": "Turnover affected comment",
"6": "Expect turnover to stay the same",
"7": "Not applicable"
},
"flushed": false,
"metadata": {
"ref_period_end_date": "2016-05-31",
"ref_period_start_date": "2016-05-01",
"ru_ref": "11842491738S",
"user_id": "UNKNOWN"
},
"origin": "uk.gov.ons.edc.eq",
"started_at": "2020-03-23T10:45:54.331913",
"submitted_at": "2020-03-23T10:49:52.869221",
"survey_id": "283",
"tx_id": "c37a3efa-593c-4bab-b49c-bee0613c4fb4",
"type": "uk.gov.ons.edc.eq:surveyresponse",
"version": "0.0.1"
}'''

        actual = '{"version": "1", "files": [{"name": "c37a3efa-593c-4bab-b49c-bee0613c4fb4.json", "URL": "http://sdx-store:5000/responses/c37a3efa-593c-4bab-b49c-bee0613c4fb4", "sizeBytes": "2135", "md5sum": "09da1a5f13ae89789d75a96db61a91d4"}], "sensitivity": "High", "sourceName": "sdx_development", "manifestCreated": "2020-12-10T11:09:29.148Z", "description": "283 survey response for period 201605 sample unit 11842491738S", "iterationL1": "201605", "dataset": "283", "schemaversion": "1"}'
        message = publish_dap.create_dap_message(json.loads(data))
        print(message)
        # self.assertEqual(message, actual)
