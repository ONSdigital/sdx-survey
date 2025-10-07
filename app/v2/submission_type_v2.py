from sdx_gcp.errors import DataError

from app.definitions.v2_context_type import V2ContextType
from app.definitions.v2_survey_type import V2SurveyType
from app.services.period import Period
from app.response import Response, ResponseType

DAP_SURVEY = ["283"]
LEGACY_SURVEY = ["009", "017", "019", "061", "127", "132", "133", "134",
                 "139", "144", "156", "160", "165", "169", "171", "182", "183", "184",
                 "185", "187", "202", "228"]
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


def get_v2_survey_type(response: Response) -> V2SurveyType:
    if response.get_response_type() == ResponseType.FEEDBACK:
        return V2SurveyType.FEEDBACK

    if _spp_submission(response):
        return V2SurveyType.SPP

    survey_id = response.get_survey_id()

    if survey_id in DAP_SURVEY:
        return V2SurveyType.DAP

    if survey_id in DEXTA_SURVEY:
        return V2SurveyType.DEXTA

    if survey_id in LEGACY_SURVEY:
        return V2SurveyType.LEGACY

    if survey_id in ENVIRONMENTAL_SURVEY:
        return V2SurveyType.ENVIRONMENTAL

    if survey_id in MATERIALS_SURVEY:
        return V2SurveyType.MATERIALS

    if survey_id in ADHOC_SURVEY:
        return V2SurveyType.ADHOC

    raise DataError(f"Survey id {survey_id} not known!")


def get_v2_context_type(survey_type: V2SurveyType) -> V2ContextType:
    if survey_type == V2SurveyType.ADHOC:
        return V2ContextType.ADHOC_SURVEY
    else:
        return V2ContextType.BUSINESS_SURVEY


def _spp_submission(response: Response) -> bool:
    if response.get_survey_id() in TO_SPP_PERIOD.keys():
        period_to_start = TO_SPP_PERIOD.get(response.get_survey_id())
        if period_to_start is not None:
            if Period(response.get_period()) >= Period(period_to_start):
                return True
    elif response.get_survey_id() in SPP_SURVEY:
        return True

    return False
