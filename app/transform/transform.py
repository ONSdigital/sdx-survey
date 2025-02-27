from typing import TypedDict

from app.response import Response
from app.submission_type import requires_pck, v2_nifi_message_submission
from app.transform import image, index, pck, idbr, json

from app.transform.zip import create_zip


class Paths(TypedDict):
    pck: str
    image: str
    index: str
    receipt: str
    json: str


class Transformer:

    def __init__(self, paths: Paths):
        self._paths = paths

    def create_zip(self, response: Response) -> bytes:
        files: dict[str, bytes] = {}
        # PCK
        if requires_pck(response):
            files[f"{self._paths['pck']}{pck.get_name(response)}"] = pck.get_contents(response)

        # Image
        image_name = image.get_name(response)
        files[f"{self._paths['image']}{image_name}"] = image.get_image(response)

        # Index
        files[f"{self._paths['index']}{index.get_name(response)}"] = index.get_contents(response, image_name)

        # IDBR Receipt
        files[f"{self._paths['receipt']}{idbr.get_name(response)}"] = idbr.get_contents(response)

        # Original json
        files[f"{self._paths['json']}{json.get_name(response)}"] = json.get_contents(response)

        return create_zip(files)


def transform(response: Response) -> bytes:

    if v2_nifi_message_submission(response):
        paths = {
            "pck": "",
            "image": "",
            "index": "",
            "receipt": "",
            "json": "",
        }
    else:
        paths = {
            "pck": "EDC_QData/",
            "image": "EDC_QImages/Images/",
            "index": "EDC_QImages/Index/",
            "receipt": "EDC_QReceipts/",
            "json": "EDC_QJson/",
        }

    transformer = Transformer(paths)
    return transformer.create_zip(response)

    # files: dict[str, bytes] = {}
    #
    # # PCK
    # if requires_pck(response):
    #     files[f"EDC_QData/{pck.get_name(response)}"] = pck.get_contents(response)
    #
    # # Image
    # image_name = image.get_name(response)
    # files[f"EDC_QImages/Images/{image_name}"] = image.get_image(response)
    #
    # # Index
    # files[f"EDC_QImages/Index/{index.get_name(response)}"] = index.get_contents(response, image_name)
    #
    # # IDBR Receipt
    # files[f"EDC_QReceipts/{idbr.get_name(response)}"] = idbr.get_contents(response)
    #
    # # Original json
    # files[f"EDC_QJson/{json.get_name(response)}"] = json.get_contents(response)
    #
    # return create_zip(files)
