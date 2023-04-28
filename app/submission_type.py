from enum import Enum

from app.errors import QuarantinableError

"""
    This file defines a set of classifiers for the different submission types.
    It also provides a set of functions for retrieving common survey metadata
    in a 'submission type' agnostic way.
"""

# list of survey ids that target only DAP
_DAP_SURVEYS = ["283", "739"]
# list of survey ids that target both DAP and Legacy
_HYBRID_SURVEYS = ["002", "007", "009", "023", "134", "147"]


class SurveyType(Enum):
    BUSINESS = 1
    ADHOC = 2


class ResponseType(Enum):
    SURVEY = 1
    FEEDBACK = 2


class SchemaVersion(Enum):
    V1 = 1
    V2 = 2


class DeliverTarget(Enum):
    LEGACY = 1
    DAP = 2
    HYBRID = 3
    FEEDBACK = 4


def get_field(submission: dict, *field_names: str) -> str:
    current = submission
    for key in field_names:
        current = current.get(key)
        if not current:
            raise QuarantinableError(f'Missing field {key} from submission!')
    return current


def get_response_type(submission: dict) -> ResponseType:
    survey_type = submission.get("type")
    if survey_type:
        if "feedback" in submission.get("type"):
            return ResponseType.FEEDBACK
    return ResponseType.SURVEY


def get_survey_type(submission: dict) -> SurveyType:
    channel = submission.get("channel")
    if channel:
        if "RH" in submission.get("channel"):
            return SurveyType.ADHOC
    return SurveyType.BUSINESS


def get_schema_version(submission: dict) -> SchemaVersion:
    version = submission.get("version")
    if version:
        if submission.get("version") == "v2":
            return SchemaVersion.V2
    return SchemaVersion.V1


def get_tx_id(submission: dict) -> str:
    return get_field(submission, "tx_id")


def get_survey_id(submission: dict) -> str:
    if get_schema_version(submission) == SchemaVersion.V2:
        return get_field(submission, "survey_metadata", "survey_id")
    else:
        return get_field(submission, "survey_id")


def get_ru_ref(submission: dict) -> str:
    if get_survey_type(submission) == SurveyType.ADHOC:
        raise QuarantinableError("Adhoc surveys do not have ru_ref field")
    if get_schema_version(submission) == SchemaVersion.V2:
        return get_field(submission, "survey_metadata", "ru_ref")
    else:
        return get_field(submission, "metadata", "ru_ref")


def get_period(submission: dict) -> str:
    if get_survey_type(submission) == SurveyType.ADHOC:
        raise QuarantinableError("Adhoc surveys do not have period field")

    if get_schema_version(submission) == SchemaVersion.V2:
        return get_field(submission, "survey_metadata", "period_id")
    else:
        return get_field(submission, "collection", "period")


def get_case_id(submission: dict) -> str:
    return get_field(submission, "case_id")


def get_user_id(submission: dict) -> str:
    if get_survey_type(submission) == SurveyType.ADHOC:
        raise QuarantinableError("Adhoc surveys do not have user_id field")

    if get_schema_version(submission) == SchemaVersion.V2:
        return get_field(submission, "survey_metadata", "user_id")
    else:
        return get_field(submission, "metadata", "user_id")


def get_deliver_target(submission: dict) -> DeliverTarget:
    if get_response_type(submission) == ResponseType.FEEDBACK:
        return DeliverTarget.FEEDBACK

    if get_survey_type(submission) == SurveyType.ADHOC:
        return DeliverTarget.DAP

    survey_id = get_survey_id(submission)
    if survey_id in _DAP_SURVEYS:
        return DeliverTarget.DAP
    elif survey_id in _HYBRID_SURVEYS:
        return DeliverTarget.HYBRID
    else:
        return DeliverTarget.LEGACY
