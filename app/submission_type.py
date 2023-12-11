from enum import Enum

from sdx_gcp.errors import DataError

from app.definitions import SurveySubmission
from sdx_gcp.app import get_logger

"""
    This file defines a set of classifiers for the different submission types.
    It also provides a set of functions for retrieving common survey metadata
    in a 'submission type' agnostic way.
"""

logger = get_logger()

# list of survey ids that target only DAP
_DAP_SURVEYS = ["283", "738", "739"]

# list of survey ids that target both DAP and Legacy
_HYBRID_SURVEYS = ["002", "007", "009", "023", "134", "147"]

# list of surveys that require a PCK file
_PCK_SURVEYS = ['009', '017', '019', '073', '074', '127', '134', '139', '144', '160', '165', '169', '171',
                '182', '183', '184', '185', '187', '202', '228']

# surveys that still use SDX transform
_LEGACY_TRANSFORMER = ['002', '092']

# surveys that need to remain v1 submissions
_V1_SURVEYS = ["283", "002", "007", "009", "023", "134", "147"]

# prepop surveys
_PREPOP_SURVEYS = ["068", "071"]


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


def requires_v1_conversion(submission: SurveySubmission) -> bool:
    if get_response_type(submission) == ResponseType.FEEDBACK:
        return False
    if get_schema_version(submission) == SchemaVersion.V1:
        return False
    return get_survey_id(submission) in _V1_SURVEYS


def requires_legacy_transform(submission: SurveySubmission) -> bool:
    return get_survey_id(submission) in _LEGACY_TRANSFORMER


def requires_pck(submission: SurveySubmission) -> bool:
    return get_survey_id(submission) in _PCK_SURVEYS


def prepop_submission(submission: SurveySubmission) -> bool:
    return get_survey_id(submission) in _PREPOP_SURVEYS


def get_field(submission: dict, *field_names: str) -> str:
    current = submission
    for key in field_names:
        current = current.get(key)
        if current is None:
            logger.error(f'Missing field {key} from submission!', submission=get_safe_submission(submission))
            raise DataError(f'Missing field {key} from submission!')
    return current


def get_form_type(submission: dict) -> ResponseType:
    return get_field(submission, "survey_metadata", "form_type")


def get_period_start_date(submission: dict) -> ResponseType:
    if get_schema_version(submission) == SchemaVersion.V2:
        return get_field(submission, "survey_metadata", "ref_p_start_date")

    return get_field(submission, "metadata", "ref_period_start_date")


def get_period_end_date(submission: dict) -> ResponseType:
    if get_schema_version(submission) == SchemaVersion.V2:
        return get_field(submission, "survey_metadata", "ref_p_end_date")

    return get_field(submission, "metadata", "ref_period_end_date")


def get_response_type(submission: dict) -> ResponseType:
    survey_type = submission.get("type")
    if survey_type:
        if "feedback" in submission.get("type"):
            return ResponseType.FEEDBACK
    return ResponseType.SURVEY


def get_submitted_at(submission: dict) -> str:
    return get_field(submission, "submitted_at")


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


def get_data(submission: dict) -> str:
    return get_field(submission, "data")


def get_qid(submission: dict) -> str:
    return get_field(submission, "survey_metadata", "qid")


def get_survey_id(submission: dict) -> str:
    if get_schema_version(submission) == SchemaVersion.V2:
        return get_field(submission, "survey_metadata", "survey_id")
    else:
        return get_field(submission, "survey_id")


def get_ru_ref(submission: dict) -> str:
    if get_survey_type(submission) == SurveyType.ADHOC:
        raise DataError("Adhoc surveys do not have ru_ref field")
    if get_schema_version(submission) == SchemaVersion.V2:
        return get_field(submission, "survey_metadata", "ru_ref")
    else:
        return get_field(submission, "metadata", "ru_ref")


def get_period(submission: dict) -> str:
    if get_survey_type(submission) == SurveyType.ADHOC:
        raise DataError("Adhoc surveys do not have period field")

    if get_schema_version(submission) == SchemaVersion.V2:
        return get_field(submission, "survey_metadata", "period_id")
    else:
        return get_field(submission, "collection", "period")


def get_case_id(submission: dict) -> str:
    return get_field(submission, "case_id")


def get_user_id(submission: dict) -> str:
    if get_survey_type(submission) == SurveyType.ADHOC:
        raise DataError("Adhoc surveys do not have user_id field")

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


def get_safe_submission(submission) -> dict:
    """
    Remove all data from the submission
    and only retain the keys / structure of the submission
    """

    if isinstance(submission, list):
        return [get_safe_submission(item) for item in submission]
    elif isinstance(submission, dict):
        return {key: get_safe_submission(value) for key, value in submission.items()}
    else:
        return ""
