import copy
import json
from typing import Any

from sdx_base.errors.errors import DataError

from app import get_logger
from app.definitions.context_type import ContextType
from app.definitions.submission import SurveySubmission, BusinessSurveyMetadata
from app.definitions.survey_type import SurveyType
from app.period import Period

"""
This file defines a wrapper for the submission.
It provides a set of functions for retrieving common survey metadata
in a 'submission type' agnostic way.
"""
logger = get_logger()

DAP_SURVEY = ["283"]
LEGACY_SURVEY = [
    "009",
    "017",
    "019",
    "061",
    "127",
    "132",
    "133",
    "134",
    "139",
    "144",
    "156",
    "160",
    "165",
    "169",
    "171",
    "182",
    "183",
    "184",
    "185",
    "187",
    "202",
    "228",
]
DEXTA_SURVEY = ["066", "073", "074", "076"]
SPP_SURVEY = ["002", "023"]
ENVIRONMENTAL_SURVEY = ["007", "147"]
MATERIALS_SURVEY = ["024", "068", "071", "194"]
ADHOC_SURVEY = ["740"]

TO_SPP_PERIOD: dict[str, str] = {
    "009": "2510",
    "139": "2512",
    "228": "2510",
}


class Response:
    def __init__(self, submission: SurveySubmission):
        self._submission = submission
        self.tx_id = submission["tx_id"]

    def get_submission(self) -> SurveySubmission:
        return copy.deepcopy(self._submission)

    def get_context_type(self) -> ContextType:
        if self.get_survey_id() in ADHOC_SURVEY:
            return ContextType.ADHOC_SURVEY
        else:
            return ContextType.BUSINESS_SURVEY

    def get_survey_type(self) -> SurveyType:
        if self.is_feedback():
            return SurveyType.FEEDBACK

        if self._spp_submission():
            return SurveyType.SPP

        survey_id = self.get_survey_id()

        if survey_id in DAP_SURVEY:
            return SurveyType.DAP

        if survey_id in DEXTA_SURVEY:
            return SurveyType.DEXTA

        if survey_id in LEGACY_SURVEY:
            return SurveyType.LEGACY

        if survey_id in ENVIRONMENTAL_SURVEY:
            return SurveyType.ENVIRONMENTAL

        if survey_id in MATERIALS_SURVEY:
            return SurveyType.MATERIALS

        if survey_id in ADHOC_SURVEY:
            return SurveyType.ADHOC

        raise DataError(f"Survey id {survey_id} not known!")

    def _spp_submission(self) -> bool:
        survey_id = self.get_survey_id()
        if survey_id in TO_SPP_PERIOD.keys():
            period_to_start = TO_SPP_PERIOD.get(survey_id)
            if period_to_start is not None:
                if Period(self.get_period()) >= Period(period_to_start):
                    return True
        elif survey_id in SPP_SURVEY:
            return True

        return False

    def to_v1_json(self) -> str:
        logger.info("Retrieving submission as V1")
        submission = self._submission
        metadata: BusinessSurveyMetadata = submission["survey_metadata"]
        v1_template = {
            "case_id": submission["case_id"],
            "tx_id": submission["tx_id"],
            "type": submission["type"],
            "version": submission["data_version"],
            "origin": submission["origin"],
            "survey_id": metadata["survey_id"],
            "flushed": submission["flushed"],
            "submitted_at": submission["submitted_at"],
            "collection": {
                "exercise_sid": submission["collection_exercise_sid"],
                "schema_name": submission["schema_name"],
                "period": metadata["period_id"],
                "instrument_id": metadata["form_type"],
            },
            "metadata": {
                "user_id": metadata["user_id"],
                "ru_ref": metadata["ru_ref"],
                "ref_period_start_date": metadata["ref_p_start_date"],
                "ref_period_end_date": metadata["ref_p_end_date"],
            },
            "launch_language_code": submission["launch_language_code"],
            "data": submission["data"],
            "form_type": metadata["form_type"],
            "started_at": submission["started_at"],
            "submission_language_code": submission["submission_language_code"],
        }

        return json.dumps(v1_template)

    def to_json(self) -> str:
        return json.dumps(self._submission)

    def get_tx_id(self) -> str:
        return self.tx_id

    def get_form_type(self) -> str:
        return self._submission["survey_metadata"]["form_type"]

    def get_period_start_date(self) -> str:
        return self._submission["survey_metadata"]["ref_p_start_date"]

    def get_period_end_date(self) -> str:
        return self._submission["survey_metadata"]["ref_p_end_date"]

    def is_feedback(self) -> bool:
        survey_type = self._submission.get("type")
        if survey_type:
            if "feedback" in self._submission.get("type"):
                return True
        return False

    def get_submitted_at(self) -> str:
        return self._submission["submitted_at"]

    def is_adhoc(self) -> bool:
        channel = self._submission.get("channel")
        if channel:
            if "RH" in self._submission.get("channel"):
                return True
        return False

    def get_data(self) -> dict[str, str] | list[Any]:
        return self._submission["data"]

    def get_data_version(self) -> str:
        return self._submission["data_version"]

    def get_qid(self) -> str:
        return self._submission["survey_metadata"]["qid"]

    def get_survey_id(self) -> str:
        return self._submission["survey_metadata"]["survey_id"]

    def get_ru_ref(self) -> str:
        if self.get_survey_type() == SurveyType.ADHOC:
            raise DataError("Adhoc surveys do not have ru_ref field")

        return self._submission["survey_metadata"]["ru_ref"]

    def get_period(self) -> str:
        return self._submission["survey_metadata"]["period_id"]

    def get_case_id(self) -> str:
        return self._submission["case_id"]

    def get_user_id(self) -> str:
        if self.get_survey_type() == SurveyType.ADHOC:
            raise DataError("Adhoc surveys do not have user_id field")

        return self._submission["survey_metadata"]["user_id"]

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
