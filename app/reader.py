from app import CONFIG
import structlog

logger = structlog.get_logger()


def read(filename) -> bytes:
    """
    Retrieve a survey response from the survey response input bucket
    """
    logger.info('Reading Survey Response file from bucket')
    blob = CONFIG.BUCKET.blob(filename)
    data_bytes = blob.download_as_bytes()

    return data_bytes
