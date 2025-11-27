import io
import zipfile


def unzip(data_bytes: bytes) -> dict[str, bytes]:
    # Create a BytesIO object from the bytes
    zip_file = io.BytesIO(data_bytes)
    results: dict[str, bytes] = {}

    # Open the zip file
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        # List the filenames of the zip file
        for name in zip_ref.namelist():
            results[name] = zip_ref.read(name)

    return results
