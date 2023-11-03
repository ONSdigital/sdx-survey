import json

from sdx_gcp.errors import DataError
from sdx_gcp.app import get_logger

from app.definitions import SurveySubmission
from app.submission_type import get_field, get_survey_type, SurveyType, get_response_type, ResponseType, \
    get_schema_version, SchemaVersion, get_deliver_target, DeliverTarget
from app.transform.formatter import get_tx_code

logger = get_logger()

SubmissionV1 = dict[str, str | dict[str, str]]


def get_optional(submission: dict, *field_names: str) -> str:
    try:
        return get_field(submission, *field_names)

    except DataError as e:
        logger.warn(str(e))
        return ""


def get_contents(submission: SurveySubmission) -> bytes:

    new_submission = submission
    if requires_converting(submission):
        new_submission = convert_v2_to_v1(submission)

    return bytes(json.dumps(new_submission))


def get_name(submission: SurveySubmission):
    return "{0}_{1}.json".format(submission["survey_metadata"]["survey_id"], get_tx_code(submission["tx_id"]))


def requires_converting(submission: SurveySubmission) -> bool:

    if get_survey_type(submission) != SurveyType.BUSINESS:
        return False

    if get_response_type(submission) != ResponseType.SURVEY:
        return False

    if get_schema_version(submission) != SchemaVersion.V2:
        return False

    if get_deliver_target(submission) == DeliverTarget.LEGACY:
        return False

    return True


def convert_v2_to_v1(submission: SurveySubmission) -> SubmissionV1:
    logger.info("Converting from v2 to v1")

    v1_template = {
        "case_id": get_field(submission, "case_id"),
        "tx_id": get_field(submission, "tx_id"),
        "type": get_field(submission, "type"),
        "version": get_field(submission, "data_version"),
        "origin": get_optional(submission, "origin"),
        "survey_id": get_field(submission, "survey_metadata", "survey_id"),
        "flushed": get_optional(submission, "flushed"),
        "submitted_at": get_field(submission, "submitted_at"),
        "collection": {
            "exercise_sid": get_field(submission, "collection_exercise_sid"),
            "schema_name": get_field(submission, "schema_name"),
            "period": get_field(submission, "survey_metadata", "period_id"),
            "instrument_id": get_field(submission, "survey_metadata", "form_type")
        },
        "metadata": {
            "user_id": get_field(submission, "survey_metadata", "user_id"),
            "ru_ref": get_field(submission, "survey_metadata", "ru_ref"),
            "ref_period_start_date": get_field(submission, "survey_metadata", "ref_p_start_date"),
            "ref_period_end_date": get_field(submission, "survey_metadata", "ref_p_end_date")
        },
        "launch_language_code": get_optional(submission, "launch_language_code"),
        "data": get_field(submission, "data"),
        "form_type": get_field(submission, "survey_metadata", "form_type"),
        "started_at": get_optional(submission, "started_at"),
        "submission_language_code": get_optional(submission, "submission_language_code")
    }

    return v1_template
