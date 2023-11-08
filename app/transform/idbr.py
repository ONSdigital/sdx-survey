from app.definitions import SurveySubmission
from app.transform.formatter import get_tx_code, split_ru_ref, get_datetime, format_date, get_period


def _idbr_receipt(survey_id, ru_ref, ru_check, period):
    """Format a receipt in IDBR format."""
    return "{0}:{1}:{2:03}:{3}".format(ru_ref, ru_check, int(survey_id), get_period(period))


def get_contents(submission: SurveySubmission) -> bytes:
    ru_ref, ru_check = split_ru_ref(submission["survey_metadata"]["ru_ref"])
    return bytes(_idbr_receipt(submission['survey_metadata']['survey_id'],
                               ru_ref, ru_check, submission['survey_metadata']['period_id']), 'utf-8')


def get_name(submission: SurveySubmission) -> str:
    d = get_datetime(submission["submitted_at"])
    return "REC{0}_{1}.DAT".format(format_date(d, "%d%m"), get_tx_code(submission["tx_id"]))
