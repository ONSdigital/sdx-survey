import datetime

from app import CONFIG
from app.response import Response
from app.transform.formatter import format_date, get_tx_code, get_datetime, get_period, split_ru_ref


def get_name(response: Response) -> str:

    survey_id = response.get_survey_id()
    submission_date = get_datetime(response.get_submitted_at())
    submission_date_str = format_date(submission_date, "%Y%m%d")
    tx_id = response.get_tx_id()
    return "EDC_{0}_{1}_{2}.csv".format(survey_id, submission_date_str, get_tx_code(tx_id))


def get_contents(response: Response, image_name: str) -> bytes:
    """Builds the contents of the index file"""

    now = datetime.datetime.utcnow()

    short_time = format_date(now, "%Y%m%d")
    long_time = format_date(now, '%d/%m/%Y %H:%M:%S')

    survey_id = response.get_survey_id()
    form_type = response.get_form_type()
    ru_ref = split_ru_ref(response.get_ru_ref())[0]
    period = get_period(response.get_period())

    image_path = CONFIG.FTP_PATH + "EDC_QImages" + "\\Images"
    # image_name_without_ext
    x = image_name.split(".")[0]

    return bytes(
        f"{long_time}, {image_path}\\{image_name}, {short_time}, {x}, {survey_id}, {form_type}, {ru_ref}, {period}, 001, 0", 'utf-8'
    )
