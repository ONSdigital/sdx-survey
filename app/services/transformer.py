from app.definitions.survey_type import V2SurveyType
from app.definitions.transform import TransformServiceBase
from app.response import Response
from app.transformation.transformers import Transformer, LegacyTransformer, MaterialsTransformer, SPPTransformer, \
    DAPTransformer, FeedbackTransformer, EnvironmentalTransformer
from app.submission_type import get_v2_survey_type


v2_transformer_map: dict[V2SurveyType, Transformer] = {
    V2SurveyType.LEGACY: LegacyTransformer(),
    V2SurveyType.MATERIALS: MaterialsTransformer(),
    V2SurveyType.SPP: SPPTransformer(),
    V2SurveyType.DAP: DAPTransformer(),
    V2SurveyType.FEEDBACK: FeedbackTransformer(),
    V2SurveyType.ENVIRONMENTAL: EnvironmentalTransformer(),
    V2SurveyType.DEXTA: LegacyTransformer()
}


class TransformService(TransformServiceBase):

    def transform(self, response: Response) -> bytes:
        v2_survey_type: V2SurveyType = get_v2_survey_type(response)
        transformer = self._get_transformer(v2_survey_type)
        return transformer.create_zip(response)

    def _get_transformer(self, survey_type: V2SurveyType) -> Transformer:
        return v2_transformer_map[survey_type]
