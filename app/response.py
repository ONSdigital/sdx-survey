import json
from enum import Enum

from sdx_gcp.app import get_logger
from sdx_gcp.errors import DataError

from app.definitions import SurveySubmission

"""
    This file defines a wrapper for the submission.
    It provides a set of functions for retrieving common survey metadata
    in a 'submission type' agnostic way.
"""
logger = get_logger()


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
        if current is None:
            logger.error(f'Missing field {key} from submission!', submission=get_safe_submission(submission))
            raise DataError(f'Missing field {key} from submission!')
    return current


class Response:

    def __init__(self, submission: SurveySubmission):
        self._submission = submission

    def get_submission(self) -> SurveySubmission:
        return self._submission

    def to_json(self) -> str:
        return json.dumps(self._submission)

    def get_tx_id(self) -> str:
        return get_field(self._submission, "tx_id")

    def get_form_type(self) -> str:
        return get_field(self._submission, "survey_metadata", "form_type")

    def get_period_start_date(self) -> str:
        if self.get_schema_version() == SchemaVersion.V2:
            return get_field(self._submission, "survey_metadata", "ref_p_start_date")

        return get_field(self._submission, "metadata", "ref_period_start_date")

    def get_period_end_date(self) -> str:
        if self.get_schema_version() == SchemaVersion.V2:
            return get_field(self._submission, "survey_metadata", "ref_p_end_date")

        return get_field(self._submission, "metadata", "ref_period_end_date")

    def get_response_type(self) -> ResponseType:
        survey_type = self._submission.get("type")
        if survey_type:
            if "feedback" in self._submission.get("type"):
                return ResponseType.FEEDBACK
        return ResponseType.SURVEY

    def get_submitted_at(self) -> str:
        return get_field(self._submission, "submitted_at")

    def get_survey_type(self) -> SurveyType:
        channel = self._submission.get("channel")
        if channel:
            if "RH" in self._submission.get("channel"):
                return SurveyType.ADHOC
        return SurveyType.BUSINESS

    def get_schema_version(self) -> SchemaVersion:
        version = self._submission.get("version")
        if version:
            if self._submission.get("version") == "v2":
                return SchemaVersion.V2
        return SchemaVersion.V1

    def get_data(self) -> dict[str, str] | list[any]:
        return self._submission["data"]

    def get_qid(self) -> str:
        return get_field(self._submission, "survey_metadata", "qid")

    def get_survey_id(self) -> str:
        if self.get_schema_version() == SchemaVersion.V2:
            return get_field(self._submission, "survey_metadata", "survey_id")
        else:
            return get_field(self._submission, "survey_id")

    def get_ru_ref(self) -> str:
        if self.get_survey_type() == SurveyType.ADHOC:
            raise DataError("Adhoc surveys do not have ru_ref field")
        if self.get_schema_version() == SchemaVersion.V2:
            return get_field(self._submission, "survey_metadata", "ru_ref")
        else:
            return get_field(self._submission, "metadata", "ru_ref")

    def get_period(self) -> str:
        if self.get_survey_type() == SurveyType.ADHOC:
            raise DataError("Adhoc surveys do not have period field")

        if self.get_schema_version() == SchemaVersion.V2:
            return get_field(self._submission, "survey_metadata", "period_id")
        else:
            return get_field(self._submission, "collection", "period")

    def get_case_id(self) -> str:
        return get_field(self._submission, "case_id")

    def get_user_id(self) -> str:
        if self.get_survey_type() == SurveyType.ADHOC:
            raise DataError("Adhoc surveys do not have user_id field")

        if self.get_schema_version() == SchemaVersion.V2:
            return get_field(self._submission, "survey_metadata", "user_id")
        else:
            return get_field(self._submission, "metadata", "user_id")


def get_safe_submission(submission) -> dict | list | str:
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