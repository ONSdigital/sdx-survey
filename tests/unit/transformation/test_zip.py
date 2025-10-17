import unittest


from app.transformation.zip import create_zip
from tests import unzip


class TestZip(unittest.TestCase):
    def test_zip(self):
        my_files = {
            "file1": b"contents for file 1",
            "subdir/file2": b"contents for file 2",
            "subdir/file3": b"contents for file 3",
        }

        zip_archive: bytes = create_zip(my_files)

        result = unzip(zip_archive)

        self.assertDictEqual(my_files, {k: v for k, v in result.items()})
