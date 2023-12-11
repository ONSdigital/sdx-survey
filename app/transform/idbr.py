from app.definitions import SurveySubmission
from app.submission_type import get_submitted_at, get_tx_id, get_ru_ref, get_survey_id
from app.submission_type import get_period as get_period_id
from app.transform.formatter import get_tx_code, split_ru_ref, get_datetime, format_date, get_period


def _idbr_receipt(survey_id, ru_ref, ru_check, period):
    """Format a receipt in IDBR format."""
    return "{0}:{1}:{2:03}:{3}".format(ru_ref, ru_check, int(survey_id), get_period(period))


def get_contents(submission: SurveySubmission) -> bytes:
    ru_ref, ru_check = split_ru_ref(get_ru_ref(submission))
    return bytes(_idbr_receipt(get_survey_id(submission),
                               ru_ref, ru_check, get_period_id(submission)), 'utf-8')


def get_name(submission: SurveySubmission) -> str:
    d = get_datetime(get_submitted_at(submission))
    return "REC{0}_{1}.DAT".format(format_date(d, "%d%m"), get_tx_code(get_tx_id(submission)))
