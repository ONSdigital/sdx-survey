from app.response import Response
from app.transform.formatter import get_tx_code, split_ru_ref, get_datetime, format_date, get_period


def _idbr_receipt(survey_id, ru_ref, ru_check, period):
    """Format a receipt in IDBR format."""
    return "{0}:{1}:{2:03}:{3}".format(ru_ref, ru_check, int(survey_id), get_period(period))


def get_contents(response: Response) -> bytes:
    ru_ref, ru_check = split_ru_ref(response.get_ru_ref())
    return bytes(_idbr_receipt(response.get_survey_id(),
                               ru_ref, ru_check, response.get_period()), 'utf-8')


def get_name(response: Response) -> str:
    d = get_datetime(response.get_submitted_at())
    return "REC{0}_{1}.DAT".format(format_date(d, "%d%m"), get_tx_code(response.get_tx_id()))
