from app.response import Response
from app.submission_type import requires_pck, spp_submission, v2_nifi_message_submission
from app.transform import image, index, pck, idbr, json, spp

from app.transform.zip import create_zip


def transform(response: Response) -> bytes:
    if v2_nifi_message_submission(response):
        return _create_zip_for_v2_message(response)

    return _create_zip_for_v1_message(response)


def _create_zip_for_v1_message(response: Response) -> bytes:
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


def _create_zip_for_v2_message(response: Response) -> bytes:
    files: dict[str, bytes] = {}

    # Original json
    files[json.get_name(response)] = json.get_contents(response)

    # PCK or SPP
    if requires_pck(response):
        files[pck.get_name(response)] = pck.get_contents(response)
    elif spp_submission(response):
        spp_contents = spp.get_contents(response)
        files[spp.get_name(response)] = spp_contents
        # Overwrite original json
        files[json.get_name(response)] = spp_contents

    # Image
    image_name = image.get_name(response)
    files[image_name] = image.get_image(response)

    # Index
    files[index.get_name(response)] = index.get_contents(response, image_name)

    # IDBR Receipt
    files[idbr.get_name(response)] = idbr.get_contents(response)

    return create_zip(files)
