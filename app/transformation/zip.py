from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED


def create_zip(files: dict[str, bytes]) -> bytes:
    """
    Takes a dictionary that maps the name of the file, to its contents
    and converts it to a zip file in memory.
    """
    archive = BytesIO()

    with ZipFile(archive, "w", ZIP_DEFLATED, False) as zip_archive:
        for filename, file_contents in files.items():
            zip_archive.writestr(filename, file_contents)

    archive.seek(0)

    return archive.read()
