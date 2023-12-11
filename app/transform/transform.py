from app.response import Response
from app.submission_type import requires_pck
from app.transform import image, index, pck, idbr, json

from app.transform.zip import create_zip


def transform(response: Response) -> bytes:
    files: dict[str, bytes] = {}

    # PCK
    if requires_pck(response):
        files[f"EDC_QData/{pck.get_name(response)}"] = pck.get_contents(response)

    # Image
    image_name = image.get_name(response)
    files[f"EDC_QImages/Images/{image_name}"] = image.get_image(response)

    # Index
    files[f"EDC_QImages/Index/{index.get_name(response)}"] = index.get_contents(response, image_name)

    # IDBR Receipt
    files[f"EDC_QReceipts/{idbr.get_name(response)}"] = idbr.get_contents(response)

    # Original json
    files[f"EDC_QJson/{json.get_name(response)}"] = json.get_contents(response)

    return create_zip(files)
