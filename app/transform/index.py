import datetime

from app import CONFIG
from app.transform.formatter import format_date, get_tx_code, get_datetime, get_period, split_ru_ref
from app.definitions import SurveySubmission


def get_name(submission: SurveySubmission) -> str:

    survey_id = submission["survey_metadata"]["survey_id"]
    submission_date = get_datetime(submission["submitted_at"])
    submission_date_str = format_date(submission_date, "%Y%m%d")
    tx_id = submission["tx_id"]
    return "EDC_{0}_{1}_{2}.csv".format(survey_id, submission_date_str, get_tx_code(tx_id))


def get_contents(submission: SurveySubmission, image_name: str) -> bytes:
    """Builds the contents of the index file"""

    now = datetime.datetime.utcnow()

    creation_time_short = format_date(now, "%Y%m%d")
    creation_time_long = format_date(now, '%d/%m/%Y %H:%M:%S')

    survey_id = submission["survey_metadata"]["survey_id"]
    instrument_id = submission["survey_metadata"]["form_type"]
    ru_ref = split_ru_ref(submission["survey_metadata"]["ru_ref"])[0]
    period = get_period(submission["survey_metadata"]["period_id"])

    image_path = CONFIG.FTP_PATH + "EDC_QImages" + "\\Images"

    return bytes(f"{creation_time_long},{image_path}\\{image_name},{creation_time_short},{image_name},{survey_id},{instrument_id},{ru_ref},{period},0", 'utf-8')
