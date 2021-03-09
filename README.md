# sdx-survey

[![Build Status](https://github.com/ONSdigital/sdx-survey/workflows/Build/badge.svg)](https://github.com/ONSdigital/sdx-survey) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/0d8f1899b0054322b9d0ec8f2bd62d86)](https://www.codacy.com/app/ons-sdc/sdx-survey?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ONSdigital/sdx-survey&amp;utm_campaign=Badge_Grade) [![codecov](https://codecov.io/gh/ONSdigital/sdx-survey/branch/main/graph/badge.svg)](https://codecov.io/gh/ONSdigital/sdx-survey)

The SDX-Survey service is used within the Office National of Statistics (ONS) for managing survey submissions in JSON
format. Surveys coming from EQ require validation and additional processing depending on their destination downstream.

## Process

The sdx-survey microservice receives survey submissions via a PubSub subscription: `survey-subscription`. Once received, 
data is decrypted and validated using PGP and voluptuous respectively. If a survey fails either step it is published to
the quarantine PubSub topic: `quarantine-survey-topic`. 

Checks are then made on the survey type; if `type: surveyresponse`, comments are extracted and stored via GCP Datastore and 
surveys requiring transformation are sent to SDX-Transform via HTTP. Once transformed, the data is sent to SDX-Deliver
via `<HTTP Post>` request and a receipt is published to PubSub: `receipt-topic`, notifying Ras-Rm that the data has been
successfully processed. For feedback submissions: `type: feedback`, no additional processing is required and the 
`deliver/feedback` endpoint on sdx-deliver is called after decryption and validation.

**Note:** Refer to Collect.py

## Getting started
Install requirements:
```shell
$ make build
```

Testing:
ensure you have installed all requirements with above `make build` command then:
```shell
$ make test
```

Running:
ensure you have installed all requirements with above `make build` command then:
```shell
$ make start
```

## GCP

#### Pubsub

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

#### Datastore
Survey writes comments into GCP Datastore under the **'Comments'** entity.

| Attribute       | Description                  | Example
|-----------------|------------------------------|----------------
| key (name/id)   | Transaction ID (tx_id)       | `name=09bd7d53-6f16-4efa-a9c0-ea6c35976062`
| created         | Date and time comment stored | `yyyy-mm-dd HH:MM:SS.ss`
| encrypted_data  | Encrypted JSON               | `gAAAAABgOR2_QLs62GL7DFp0Fr_DwRatIQlWK...`
| period          | Period from survey JSON      | `period: 201904`
| survey_id       | Survey ID                    | `survey_id: 017`


#### Secret Manager
The `sdx-survey-decrypt` and `sdx-comment-key` are managed by Google Secret Manager. A single API call is made on program startup
and each are stored in `DECRYPT_SURVEY_KEY` and `ENCRYPT_COMMENT_KEY` respectively.

## License

Copyright © 2016, Office for National Statistics (https://www.ons.gov.uk)

Released under MIT license, see [LICENSE](LICENSE) for details.
