from app.definitions.v2_survey_type import V2SurveyType
from app.response import Response
from app.submission_type import requires_pck, v2_nifi_message_submission
from app.transformation.transformers import Transformer, LegacyTransformer, MaterialsTransformer, SPPTransformer, \
    DAPTransformer, FeedbackTransformer, EnvironmentalTransformer
from app.transformation.transforms import idbr, image, index, json, pck

from app.transformation.zip import create_zip
from app.v2.submission_type_v2 import get_v2_survey_type


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


v2_transformer_map: dict[V2SurveyType, Transformer] = {
    V2SurveyType.LEGACY: LegacyTransformer(),
    V2SurveyType.MATERIALS: MaterialsTransformer(),
    V2SurveyType.SPP: SPPTransformer(),
    V2SurveyType.DAP: DAPTransformer(),
    V2SurveyType.FEEDBACK: FeedbackTransformer(),
    V2SurveyType.ENVIRONMENTAL: EnvironmentalTransformer(),
}


def _get_transformer(survey_type: V2SurveyType) -> Transformer:
    return v2_transformer_map[survey_type]


def _create_zip_for_v2_message(response: Response) -> bytes:
    v2_survey_type: V2SurveyType = get_v2_survey_type(response)

    transformer = _get_transformer(v2_survey_type)

    return transformer.create_zip(response)
