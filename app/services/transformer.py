from app.definitions.transformer import TransformerBase
from app.response import Response
from app.transformation.selector import TransformSelector
from app.transformation.zip import create_zip


class TransformService(TransformerBase):

    def __init__(self, transform_selector: TransformSelector):
        self._transform_selector = transform_selector

    def transform(self, response: Response) -> bytes:
        files: dict[str, bytes] = {}
        transform_list = self._transform_selector.select(response.get_survey_type())

        for transform in transform_list:
            name = transform.get_file_name(response)
            content = transform.get_file_content(response)

            files[name] = content

        return create_zip(files)
