import logging

from functools import partial
from voluptuous import Schema, Required, Length, All, MultipleInvalid, Optional
from structlog import wrap_logger
from dateutil import parser
from uuid import UUID

from app.errors import ClientError

logger = wrap_logger(logging.getLogger(__name__))

KNOWN_SURVEYS = {
    "0.0.1": {
        "009": [
            "0106", "0111", "0117", "0123", "0158", "0161", "0167", "0173", "0201", "0202",
            "0203", "0204", "0205", "0216", "0251", "0253", "0255", "0817", "0823", "0867",
            "0873",
        ],
        "017": [
            "0001", "0002", "0003", "0004", "0005", "0006", "0007", "0008", "0009", "0010",
            "0011", "0012", "0013", "0014", "0033", "0034", "0051", "0052", "0057", "0058",
            "0061", "0070"
        ],
        "019": ["0018", "0019", "0020"],
        "023": ["0203", "0213", "0205", "0215", "0102", "0112"],
        "134": ["0005"],
        "139": ["0001"],
        "144": ["0001", "0002"],
        "147": ["0003", "0004"],
        "160": ["0002"],
        "165": ["0002"],
        "169": ["0003"],
        "182": ["0006"],
        "183": ["0006"],
        "184": ["0006"],
        "185": ["0005"],
        "187": ["0001", "0002", "0051"],
        "228": ["0001", "0002"],
        "283": ["0001", "0002"],
    },
    "0.0.2": {
        "census": ["household", "individual", "communal"],
        "lms": ["1", "2"],
        "281": ["0001"],
    },
}

# Parses a timestamp, throwing a value error
# if unrecognised
def Timestamp(value):
    return parser.parse(value)


def ValidSurveyId(value, version=None):
    if not version:
        raise AttributeError("No version number")

    if value not in KNOWN_SURVEYS[version]:
        raise ValueError("Invalid survey id")


# Parses a UUID, throwing a value error
# if unrecognised
def ValidSurveyTxId(value):
    return UUID(value, version=4)


def ValidSurveyData(data):
    if isinstance(data, dict):
        for k, v in data.items():
            if not isinstance(k, str) or not isinstance(v, (str, list, int, float)):
                raise ValueError("Invalid survey data")

    else:
        raise ValueError("Invalid survey data")


def ValidateListSurveyData(data):
    if not isinstance(data, list):
        raise ValueError("Invalid surey data")


def validate(survey_dict: dict) -> bool:
    try:
        json_data = survey_dict

        response_type = str(json_data["type"])

        if response_type.find("feedback") == -1:
            version = json_data["version"]

            schema = get_schema(version)

            if schema is None:
                raise ClientError("Unsupported schema version '%s'" % version)

            metadata = json_data.get("metadata")
            bound_logger = logger.bind(survey_id=json_data.get("survey_id"),
                                       tx_id=json_data.get("tx_id"),
                                       user_id=metadata.get("user_id"),
                                       ru_ref=metadata.get("ru_ref"))

            bound_logger.debug("Validating json against schema")
            schema(json_data)

            survey_id = json_data.get("survey_id")
            if survey_id not in KNOWN_SURVEYS.get(version, {}):
                bound_logger.debug("Survey id is not known", survey_id=survey_id)
                raise ClientError(f"Unsupported survey '{survey_id}'")

            instrument_id = json_data.get("collection", {}).get("instrument_id")
            if instrument_id not in KNOWN_SURVEYS.get(version, {}).get(survey_id, []):
                bound_logger.debug("Instrument ID is not known", survey_id=survey_id)
                raise ClientError(f"Unsupported instrument '{instrument_id}'")

        else:
            schema = get_schema("feedback")

            bound_logger = logger.bind(response_type="feedback", tx_id=json_data.get("tx_id"))
            bound_logger.debug("Validating json against schema")
            schema(json_data)

        bound_logger.debug("Success")

    except (MultipleInvalid, KeyError, TypeError, ValueError) as e:
        logger.error("Client error", error=e)
        raise ClientError(str(e))

    except Exception as e:
        logger.error("Server error", error=e)
        raise ClientError(e)

    return True


def get_schema(version):

    if version == "0.0.1":
        valid_survey_id = partial(ValidSurveyId, version="0.0.1")

        collection_s = Schema(
            {
                Required("period"): str,
                Required("exercise_sid"): str,
                Required("instrument_id"): All(str, Length(max=4)),
            }
        )

        metadata_s = Schema(
            {
                Required("user_id"): str,
                Required("ru_ref"): All(str, Length(12)),
                Optional("ref_period_start_date"): Timestamp,
                Optional("ref_period_end_date"): Timestamp,
            }
        )

        schema = Schema(
            {
                Required("type"): "uk.gov.ons.edc.eq:surveyresponse",
                Required("version"): "0.0.1",
                Optional("tx_id"): All(str, ValidSurveyTxId),
                Required("origin"): "uk.gov.ons.edc.eq",
                Required("survey_id"): All(str, valid_survey_id),
                Optional("case_id"): str,
                Optional("case_ref"): str,
                Optional("completed"): bool,
                Optional("flushed"): bool,
                Optional("started_at"): Timestamp,
                Required("submitted_at"): Timestamp,
                Required("collection"): collection_s,
                Required("metadata"): metadata_s,
                Required("data"): ValidSurveyData,
                Optional("paradata"): object,
            }
        )
        return schema

    elif version == "0.0.2":
        valid_survey_id = partial(ValidSurveyId, version="0.0.2")

        collection_s = Schema(
            {
                Required("period"): str,
                Required("exercise_sid"): str,
                Required("instrument_id"): All(str, Length(max=10)),
            }
        )

        metadata_s = Schema(
            {
                Required("user_id"): str,
                Optional("ru_ref"): str,
                Optional("ref_period_start_date"): Timestamp,
                Optional("ref_period_end_date"): Timestamp,
            }
        )

        schema = Schema(
            {
                Required("type"): "uk.gov.ons.edc.eq:surveyresponse",
                Required("version"): "0.0.2",
                Optional("tx_id"): All(str, ValidSurveyTxId),
                Required("origin"): "uk.gov.ons.edc.eq",
                Required("survey_id"): All(str, valid_survey_id),
                Optional("completed"): bool,
                Optional("flushed"): bool,
                Optional("started_at"): Timestamp,
                Required("submitted_at"): Timestamp,
                Required("case_id"): str,
                Optional("case_ref"): str,
                Required("collection"): collection_s,
                Required("metadata"): metadata_s,
                Required("data"): ValidateListSurveyData,
                Optional("paradata"): object,
            }
        )
        return schema

    elif version == "feedback":

        collection_s = Schema(
            {
                Required("period"): str,
                Required("exercise_sid"): str,
                Required("instrument_id"): All(str, Length(max=10)),
            }
        )

        schema = Schema(
            {
                Required("type"): "uk.gov.ons.edc.eq:feedback",
                Optional("tx_id"): All(str, ValidSurveyTxId),
                Required("origin"): "uk.gov.ons.edc.eq",
                Required("survey_id"): str,
                Required("version"): str,
                Optional("completed"): bool,
                Optional("flushed"): bool,
                Optional("started_at"): Timestamp,
                Required("submitted_at"): Timestamp,
                Required("collection"): collection_s,
                Required("data"): ValidSurveyData,
                Optional("metadata"): object,
                Optional("paradata"): object,
            }
        )
        return schema

    else:
        return None
