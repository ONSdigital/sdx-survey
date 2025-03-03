from datetime import datetime

from sdx_gcp.app import get_logger

from app.response import Response
from app.transform.call_transformer import call_transformer_spp

logger = get_logger()


def get_contents(response: Response) -> bytes:
    return call_transformer_spp(response)


def get_name(response: Response) -> str:
    survey_id = response.get_survey_id()
    tx_id = response.get_tx_id()
    timestamp = get_timestamp()

    return f"{survey_id}_SDC_{timestamp}_{tx_id}.json"


def get_timestamp() -> str:
    return get_now().strftime("%Y-%m-%dT%H-%M-%S")


def get_now() -> datetime:
    return datetime.now()