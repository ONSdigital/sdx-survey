from sdx_gcp.app import get_logger

from app.response import Response
from app.transform.call_transformer import call_transformer_spp
from app.transform.formatter import get_tx_code

logger = get_logger()


def get_contents(response: Response) -> bytes:
    return call_transformer_spp(response)


def get_name(response: Response) -> str:
    survey_id = response.get_survey_id()
    tx_id = response.get_tx_id()

    return f"{survey_id}_{get_tx_code(tx_id)}.json"
