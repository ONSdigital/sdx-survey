from io import BytesIO
import unittest
import zipfile

from app.transform.zip import create_zip


def extract_zip(zip_bytes: bytes) -> dict:
    z = zipfile.ZipFile(BytesIO(zip_bytes), "r")
    files = {}
    for filename in z.namelist():
        file_bytes = z.read(filename)
        files[filename] = file_bytes

    z.close()

    return files


class TestZip(unittest.TestCase):

    def test_zip(self):
        my_files = {
            "file1": b"contents for file 1",
            "subdir/file2": b"contents for file 2",
            "subdir/file3": b"contents for file 3"
        }

        zip_archive: bytes = create_zip(my_files)

        result = extract_zip(zip_archive)

        self.assertDictEqual(my_files, {k: v for k, v in result.items()})
