from app import CONFIG
import structlog

logger = structlog.get_logger()


def quarantine_submission(tx_id: str, error: str):
    """Publish the tx_id and any details about the error to the quarantine topic"""

    logger.error("Quarantining submission")
    data = error.encode("utf-8")
    future = CONFIG.QUARANTINE_PUBLISHER.publish(CONFIG.QUARANTINE_TOPIC_PATH, data, tx_id=tx_id, error=error)
    return future.result()
