import structlog

from functools import partial
from structlog.contextvars import bind_contextvars, unbind_contextvars
from voluptuous import Schema, Required, Length, All, MultipleInvalid, Optional
from dateutil import parser
from uuid import UUID
from app.errors import QuarantinableError

logger = structlog.get_logger('app.subscriber')

# A dict of dicts containing lists of formtypes mapped to survey ids
KNOWN_SURVEYS = {
    "0.0.1": {
        "007": [
            "0010", "0009"
        ],
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
        "024": ["0002"],
        "092": ["0001"],
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
        "194": ["001"],
        "202": ["1802", "1804", "1808", "1810", "1812", "1814", "1818", "1820", "1824", "1826", "1862", "1864", "1874"],
        "228": ["0001", "0002"],
        "283": ["0001", "0002"],
    },
    "0.0.2": {
        "census": ["household", "individual", "communal"],
        "lms": ["1", "2"],
        "281": ["0001"],
    },
}


def parse_timestamp(value):
    """Parses a timestamp, throwing a value error if unrecognised"""
    return parser.parse(value)


def is_valid_survey_id(value, version=None):
    """Tests if a survey id is valid"""
    if not version:
        raise AttributeError("No version number")

    if value not in KNOWN_SURVEYS[version]:
        raise ValueError("Invalid survey id")


def is_valid_survey_txid(value):
    """Parses a UUID, throwing a value error if unrecognised"""
    return UUID(value, version=4)


def is_valid_survey_data(data):
    """Tests if a survey data is of valid types"""
    if isinstance(data, dict):
        for k, v in data.items():
            if not isinstance(k, str) or not isinstance(v, (str, list, int, float)):
                raise ValueError("Invalid survey data")

    else:
        raise ValueError("Invalid survey data")


def is_valid_list_survey_data(data):
    if not isinstance(data, list):
        raise ValueError("Invalid survey data")


def validate(survey_dict: dict) -> bool:
    """
    Validates every aspect of a survey submission in dictionary form.
    Returns True if valid or raises an appropriate exception if not.
    """

    logger.info(f"Validating")
    try:
        json_data = survey_dict
        if json_data.get('type') is None:
            raise QuarantinableError('Missing type field')

        response_type = str(json_data["type"])

        if response_type.find("feedback") == -1:
            version = json_data["version"]

            schema = get_schema(version)

            if schema is None:
                raise QuarantinableError("Unsupported schema version '%s'" % version)

            metadata = json_data.get("metadata")
            if metadata is None:
                raise QuarantinableError('Missing metadata field')
            bind_contextvars(survey_id=json_data.get("survey_id"),
                             user_id=metadata.get("user_id"),
                             ru_ref=metadata.get("ru_ref"))

            logger.info("Validating json against schema")
            schema(json_data)

            survey_id = json_data.get("survey_id")
            if survey_id not in KNOWN_SURVEYS.get(version, {}):
                logger.error("Survey id is not known", survey_id=survey_id)
                raise QuarantinableError(f"Unsupported survey '{survey_id}'")

            instrument_id = json_data.get("collection", {}).get("instrument_id")
            if instrument_id not in KNOWN_SURVEYS.get(version, {}).get(survey_id, []):
                logger.error("Instrument ID is not known", survey_id=survey_id)
                raise QuarantinableError(f"Unsupported instrument '{instrument_id}'")

        else:
            schema = get_schema("feedback")

            bind_contextvars(response_type="feedback")
            logger.info("Validating json against schema")
            schema(json_data)

        logger.debug("Success")

    except (MultipleInvalid, KeyError, TypeError, ValueError) as e:
        logger.error("Client error", error=e)
        raise QuarantinableError(e)

    except Exception as e:
        logger.error("Server error", error=e)
        raise QuarantinableError(e)

    logger.info(f"Validation successful")
    unbind_contextvars('survey_id',
                       'response_type',
                       'user_id',
                       'ru_ref')
    return True


def get_schema(version):
    if version == "0.0.1":
        valid_survey_id = partial(is_valid_survey_id, version="0.0.1")

        collection_s = Schema(
            {
                Required("period"): str,
                Required("exercise_sid"): str,
                Required("instrument_id"): All(str, Length(max=4)),
                # Added for eq_v3
                Optional("schema_name"): str,
            }
        )

        metadata_s = Schema(
            {
                Required("user_id"): str,
                Required("ru_ref"): All(str, Length(12)),
                Optional("ref_period_start_date"): parse_timestamp,
                Optional("ref_period_end_date"): parse_timestamp,
            }
        )

        schema = Schema(
            {
                Required("type"): "uk.gov.ons.edc.eq:surveyresponse",
                Required("version"): "0.0.1",
                Optional("tx_id"): All(str, is_valid_survey_txid),
                Required("origin"): "uk.gov.ons.edc.eq",
                Required("survey_id"): All(str, valid_survey_id),
                Optional("case_id"): str,
                Optional("case_ref"): str,
                Optional("completed"): bool,
                Optional("flushed"): bool,
                Optional("started_at"): parse_timestamp,
                Required("submitted_at"): parse_timestamp,
                Required("collection"): collection_s,
                Required("metadata"): metadata_s,
                Required("data"): is_valid_survey_data,
                Optional("paradata"): object,
                # Added for eq_v3
                Optional("case_type"): str,
                Optional("launch_language_code"): str,
                Optional("submission_language_code"): str,
                Optional("form_type"): str,
                Optional("region_code"): str,
                Optional("case_ref"): str,
                Optional("case_type"): str,
                Optional("channel"): str,
            }
        )
        return schema

    elif version == "0.0.2":
        valid_survey_id = partial(is_valid_survey_id, version="0.0.2")

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
                Optional("ref_period_start_date"): parse_timestamp,
                Optional("ref_period_end_date"): parse_timestamp,
            }
        )

        schema = Schema(
            {
                Required("type"): "uk.gov.ons.edc.eq:surveyresponse",
                Required("version"): "0.0.2",
                Optional("tx_id"): All(str, is_valid_survey_txid),
                Required("origin"): "uk.gov.ons.edc.eq",
                Required("survey_id"): All(str, valid_survey_id),
                Optional("completed"): bool,
                Optional("flushed"): bool,
                Optional("started_at"): parse_timestamp,
                Required("submitted_at"): parse_timestamp,
                Required("case_id"): str,
                Optional("case_ref"): str,
                Required("collection"): collection_s,
                Required("metadata"): metadata_s,
                Required("data"): is_valid_list_survey_data,
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
                # Added for eq_v3
                Optional("schema_name"): str,
            }
        )

        schema = Schema(
            {
                Required("type"): "uk.gov.ons.edc.eq:feedback",
                Optional("tx_id"): All(str, is_valid_survey_txid),
                Required("origin"): "uk.gov.ons.edc.eq",
                Required("survey_id"): str,
                Required("version"): str,
                Optional("completed"): bool,
                Optional("flushed"): bool,
                Optional("started_at"): parse_timestamp,
                Required("submitted_at"): parse_timestamp,
                Required("collection"): collection_s,
                Required("data"): is_valid_survey_data,
                Optional("metadata"): object,
                Optional("paradata"): object,
                # Added for eq_v3
                Optional("case_id"): str,
                Optional("launch_language_code"): str,
                Optional("submission_language_code"): str,
                Optional("form_type"): str,
            }
        )
        return schema

    else:
        return None
