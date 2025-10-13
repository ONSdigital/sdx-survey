from app import get_logger
from app.definitions.http import TransformPosterBase
from app.response import Response
from app.transformation.formatter import get_tx_code
from app.definitions.transform import Transform

logger = get_logger()


def get_name(response: Response) -> str:
    survey_id = response.get_survey_id()
    tx_id = response.get_tx_id()

    if survey_id == "202":
        survey_id = get_abs_survey_id(response.get_form_type())

    if survey_id in ["182", "183", "184", "185"]:
        survey_id = "181"

    return f"{survey_id}_{get_tx_code(tx_id)}"


# a dictionary mapping the form type to the sector id required downstream
form_map = {'1802': '053',
            '1804': '051',
            '1808': '050',
            '1810': '055',
            '1812': '052',
            '1814': '052',
            '1818': '052',
            '1820': '052',
            '1824': '052',
            '1826': '052',
            '1862': '001',
            '1864': '001',
            '1874': '001',
            '1805': '054',
            '1875': '001',
            '1865': '001',
            '1863': '001',
            '1819': '052',
            '1825': '052',
            '1806': '054',
            '1815': '052',
            '1827': '052',
            '1821': '052',
            '1867': '001',
            '1869': '001',
            '1871': '001',
            '1877': '001',
            '1879': '001',
            '1801': '053',
            '1803': '051',
            '1807': '050',
            '1809': '055',
            '1811': '052',
            '1813': '052',
            '1817': '052',
            '1823': '052',
            '1861': '001',
            '1873': '001',
            }


def get_abs_survey_id(formtype: str) -> str:
    return form_map.get(formtype)


class PCKTransform(Transform):

    def __init__(self, transformer_post: TransformPosterBase):
        self._transformer_post = transformer_post

    def get_file_name(self, response: Response) -> str:
        return get_name(response)

    def get_file_content(self, response: Response) -> bytes:
        return self._transformer_post.call_transformer_pck(response)
