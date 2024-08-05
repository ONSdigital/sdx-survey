# sdx-survey

The SDX-Survey service is used within the Office National for Statistics (ONS) for managing survey submissions in JSON
format. These submissions come from EQ and require validation and additional processing depending on their destination downstream.

## Process

The sdx-survey microservice receives a notification via a PubSub subscription: `survey-trigger-subscription`.
From this notification it reads the transaction id and then reads the corresponding file from Bucket: `survey-responses`
the data is then decrypted and validated. If a survey validation fails it is published to
the quarantine PubSub topic: `quarantine-survey-topic`. 

Checks are then made on the survey type; if `type: surveyresponse`, comments are extracted and stored via GCP Datastore. 
Additionally, surveys requiring transformation are sent to SDX-Transform via `<HTTP Post>`. 
Once transformed, the data is sent to SDX-Deliver via `<HTTP Post>` and a receipt is published to PubSub 
topic: `receipt-topic`. This receipt notifies RASRM that the data has been successfully processed. For feedback submissions: `type: feedback`, 
no additional processing is required and the `/deliver/feedback` endpoint on sdx-deliver is called after decryption and validation.

**Note:** Refer to Collect.py

## Getting started
Install pipenv:
```shell
$ pip install pipenv
```

Create a virtualenv and install dependencies
```shell
$ make build
```

Testing:
Install all test requirements and run tests:
```shell
$ make test
```

Running:
ensure you have installed all requirements with above `make build` command then:
```shell
$ make start
```

## GCP

### Pubsub

SDX-Survey receives message from `survey-subscription`. This message contains the encrypted JSON and `tx_id`

**Message Structure Example**
```code
Message {
  data: b'eyJhbGciOiJSU0EtT0FFUCIsImVuYyI6IkEyNTZHQ00iLCJraW...'
  ordering_key: ''
  attributes: {
    "tx_id": "7ef50b15-49f5-4ad3-bb08-911537d1417d"
  }
}
```

**Message Data field unencrypted**
(python dict)
```python
data : {
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
```

    
**Quarantine Message**

SDX-Survey publishes to `quarantine-survey-submission`. The original message from `survey-submission` 
is published in addition to the error/validation message 

```code
Message {
  data: b'eyJhbGciOiJSU0EtT0FFUCIsImVuYyI6IkEyNTZHQ00iLCJraW...'
  ordering_key: ''
  attributes: {
    "error": "required key not provided @ data['data']",
    "tx_id": "a79160b5-67de-460c-bda3-cc54b97c7c50"
  }
```


**RAS-RM Receipt:**
```
receipt: Message {
  data: b'{"case_id": "4c0bc9ec-06d4-4f66-88b6-2e42b79f17b3"...'
  ordering_key: ''
  attributes: {
    "tx_id": "62a18c14-5ff8-4047-8f30-7e8292df87ff"
  }
}
```
Data Field (Converted to JSON):
```json
{
    "caseId": "4c0bc9ec-06d4-4f66-88b6-2e42b79f17b3",
    "partyId": "123-456"
}
```

### Datastore
Survey writes comments into GCP Datastore under the **'{survey_id}_{period}'** kind.

| Attribute      | Description                  | Example                                     |
|----------------|------------------------------|---------------------------------------------|
| key (name/id)  | Transaction ID (tx_id)       | `name=09bd7d53-6f16-4efa-a9c0-ea6c35976062` |
| created        | Date and time comment stored | `yyyy-mm-dd, HH:MM:SS.ss`                   |
| encrypted_data | Encrypted JSON               | `gAAAAABgOR2_QLs62GL7DFp0Fr_DwRatIQlWK...`  |


### Secret Manager

The `sdx-private-jwt`,  `sdx-comment-key` and `eq-public-signing` are managed by Google Secret Manager. A single API call is made on program startup
and each are stored in `DECRYPT_SURVEY_KEY`, `ENCRYPT_COMMENT_KEY` and `AUTHENTICATE_SURVEY_KEY` respectively.


## License

Copyright © 2024, Office for National Statistics (https://www.ons.gov.uk)

Released under MIT license, see [LICENSE](LICENSE) for details.
