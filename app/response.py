import copy
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


def get_optional(submission: dict, *field_names: str) -> str:
    try:
        return get_field(submission, *field_names)

    except DataError as e:
        logger.warn(str(e))
        return ""


class Response:

    def __init__(self, submission: SurveySubmission, tx_id: str):
        self._submission = submission
        self.tx_id = tx_id

    def get_submission(self) -> SurveySubmission:
        return copy.deepcopy(self._submission)

    def to_v1_json(self) -> str:
        logger.info("Retrieving submission as V1")

        submission = self._submission
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

        return json.dumps(v1_template)

    def to_json(self) -> str:
        return json.dumps(self._submission)

    def get_tx_id(self) -> str:
        return self.tx_id

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

    def get_data_version(self) -> str:
        return self._submission["data_version"]

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

    def __eq__(self, other):
        """
        Override the equality method
        to be able to compare two Responses
        """
        if isinstance(other, Response):
            return self._submission == other._submission
        return False


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
