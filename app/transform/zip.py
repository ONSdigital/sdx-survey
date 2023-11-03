from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED


def create_zip(files: dict[str, bytes]) -> BytesIO:
    """
    :param files - A dictionary that maps the name of the file, to it's contents
    """
    archive = BytesIO()

    with ZipFile(archive, "w", ZIP_DEFLATED, False) as zip_archive:
        for filename, file_contents in files.items():
            zip_archive.writestr(filename, file_contents)

    archive.seek(0)

    return archive
