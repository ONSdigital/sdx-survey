import datetime
import dateutil.parser

from app import CONFIG
from app.transform.formatter import format_date, get_index_name
from app.definitions import SurveySubmission


def get_name(submission: SurveySubmission) -> str:

    survey_id = submission["survey_metadata"]["survey_id"]
    submission_date = dateutil.parser.parse(submission["submitted_at"])
    submission_date_str = format_date(submission_date, 'short')
    tx_id = submission["tx_id"]
    return get_index_name(survey_id, submission_date_str, tx_id)


def get_contents(submission: SurveySubmission, image_name: str) -> bytes:
    """Builds the contents of the index file"""

    now = datetime.datetime.utcnow()

    creation_time_short = format_date(now, 'short')
    creation_time_long = format_date(now)

    survey_id = submission["survey_metadata"]["survey_id"]
    instrument_id = submission["survey_metadata"]["form_type"]
    ru_ref = submission["survey_metadata"]["ru_ref"]
    period = submission["survey_metadata"]["period_id"]

    image_path = CONFIG.FTP_PATH + "EDC_QImages" + "\\Images"

    return bytes(f"{creation_time_long},{image_path}\\{image_name},{creation_time_short},{image_name},{survey_id},{instrument_id},{ru_ref},{period},0")
