import io
import unittest
import zipfile

from app.zip import create_zip


def extract_zip(zip_bytes: bytes) -> dict:
	z = zipfile.ZipFile(io.BytesIO(zip_bytes), "r")
	files = {}
	for filename in z.namelist():
		file_bytes = z.read(filename)
		files[filename] = file_bytes

	z.close()
	return files

class TestZip(unittest.TestCase):

	def test_zip(self):

		my_files = {
			"file1": "contents for file 1",
			"file2": "contents for file 2",
			"file3": "contents for file 3"
		}

		zip_contents = create_zip(my_files)

		extracted_zip_files = extract_zip(zip_contents)

		self.assertDictEqual(extracted_zip_files, my_files)