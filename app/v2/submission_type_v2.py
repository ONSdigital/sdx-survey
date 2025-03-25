from app.definitions.v2_survey_type import V2SurveyType
from app.response import Response, ResponseType

DAP_SURVEY = ["283"]
LEGACY_SURVEY = ["009", "017", "019", "066", "076", "073", "074", "127", "134",
                 "139", "144", "160", "165", "169", "171", "182", "183", "184",
                 "185", "187", "202", "228"]
SPP_SURVEY = ["002", "023"]
ENVIRONMENTAL_SURVEY = ["007", "147"]
MATERIALS_SURVEY = ["024", "068", "071", "194"]
ADHOC_SURVEY = ["740"]


def get_v2_survey_type(response: Response) -> V2SurveyType:
    if response.get_response_type() == ResponseType.FEEDBACK:
        return V2SurveyType.FEEDBACK

    survey_id = response.get_survey_id()

    if survey_id in DAP_SURVEY:
        return V2SurveyType.DAP

    if survey_id in LEGACY_SURVEY:
        return V2SurveyType.LEGACY

    if survey_id in SPP_SURVEY:
        return V2SurveyType.SPP

    if survey_id in ENVIRONMENTAL_SURVEY:
        return V2SurveyType.ENVIRONMENTAL

    if survey_id in MATERIALS_SURVEY:
        return V2SurveyType.MATERIALS

    if survey_id in ADHOC_SURVEY:
        return V2SurveyType.ADHOC
