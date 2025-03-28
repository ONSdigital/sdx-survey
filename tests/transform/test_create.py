import unittest
from unittest.mock import patch, Mock

from app.definitions.transform import Transform
from app.response import Response
from app.transform.create import transform

from app.transform.transformers.transformer import Transformer
from tests import unzip


class MockTransform1(Transform):

    def get_file_name(self, response: Response) -> str:
        return "mockFile1"

    def get_file_content(self, response: Response) -> bytes:
        return b'mockContents1'


class MockTransform2(Transform):

    def get_file_name(self, response: Response) -> str:
        return "mockFile2"

    def get_file_content(self, response: Response) -> bytes:
        return b'mockContents2'


class MockTransformer(Transformer):

    def __init__(self):
        transform_list = [MockTransform1(), MockTransform2()]
        super().__init__(transform_list)


class TestCreate(unittest.TestCase):

    @patch("app.transform.create.v2_nifi_message_submission")
    @patch("app.transform.create._get_transformer")
    def test_transform_for_v2(self, mock_get_transformer: Mock, mock_is_v2_message: Mock):
        response: Response = Mock(spec=Response)
        mock_is_v2_message.return_value = True
        mock_get_transformer.return_value = MockTransformer()
        actual: dict[str, bytes] = unzip(transform(response))
        expected: dict[str, bytes] = {
            "mockFile1": b'mockContents1',
            "mockFile2": b'mockContents2',
        }
        self.assertEqual(expected, actual)

    @patch("app.transform.create.json")
    @patch("app.transform.create.idbr")
    @patch("app.transform.create.index")
    @patch("app.transform.create.image")
    @patch("app.transform.create.pck")
    @patch("app.transform.create.v2_nifi_message_submission")
    @patch("app.transform.create.requires_pck")
    def test_transform_for_v1_with_pck(self,
                                       mock_requires_pck: Mock,
                                       mock_is_v2_message: Mock,
                                       mock_pck: Mock,
                                       mock_image: Mock,
                                       mock_index: Mock,
                                       mock_idbr: Mock,
                                       mock_json: Mock):
        response: Response = Mock(spec=Response)
        mock_requires_pck.return_value = True
        mock_is_v2_message.return_value = False

        mock_pck.get_contents.return_value = b"pck_contents"
        mock_pck.get_name.return_value = "pck_name"

        mock_image.get_image.return_value = b"image_contents"
        mock_image.get_name.return_value = "image_name"

        mock_index.get_contents.return_value = b"index_contents"
        mock_index.get_name.return_value = "index_name"

        mock_idbr.get_contents.return_value = b"idbr_contents"
        mock_idbr.get_name.return_value = "idbr_name"

        mock_json.get_contents.return_value = b"json_contents"
        mock_json.get_name.return_value = "json_name"

        actual: dict[str, bytes] = unzip(transform(response))
        expected = {
            "EDC_QData/pck_name": b"pck_contents",
            "EDC_QImages/Images/image_name": b"image_contents",
            "EDC_QImages/Index/index_name": b"index_contents",
            "EDC_QReceipts/idbr_name": b"idbr_contents",
            "EDC_QJson/json_name": b"json_contents",
        }

        self.assertEqual(expected, actual)

    @patch("app.transform.create.json")
    @patch("app.transform.create.idbr")
    @patch("app.transform.create.index")
    @patch("app.transform.create.image")
    @patch("app.transform.create.pck")
    @patch("app.transform.create.v2_nifi_message_submission")
    @patch("app.transform.create.requires_pck")
    def test_transform_for_v1_without_pck(self,
                                          mock_requires_pck: Mock,
                                          mock_is_v2_message: Mock,
                                          mock_pck: Mock,
                                          mock_image: Mock,
                                          mock_index: Mock,
                                          mock_idbr: Mock,
                                          mock_json: Mock):
        response: Response = Mock(spec=Response)
        mock_requires_pck.return_value = False
        mock_is_v2_message.return_value = False

        mock_pck.get_contents.return_value = b"pck_contents"
        mock_pck.get_name.return_value = "pck_name"

        mock_image.get_image.return_value = b"image_contents"
        mock_image.get_name.return_value = "image_name"

        mock_index.get_contents.return_value = b"index_contents"
        mock_index.get_name.return_value = "index_name"

        mock_idbr.get_contents.return_value = b"idbr_contents"
        mock_idbr.get_name.return_value = "idbr_name"

        mock_json.get_contents.return_value = b"json_contents"
        mock_json.get_name.return_value = "json_name"

        actual: dict[str, bytes] = unzip(transform(response))
        expected = {
            "EDC_QImages/Images/image_name": b"image_contents",
            "EDC_QImages/Index/index_name": b"index_contents",
            "EDC_QReceipts/idbr_name": b"idbr_contents",
            "EDC_QJson/json_name": b"json_contents",
        }

        self.assertEqual(expected, actual)
