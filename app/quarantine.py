from app import CONFIG
import structlog

logger = structlog.get_logger()

def quarantine_submission(data_str: str, tx_id: str, error):
    logger.error("Quarantining submission")
    data = data_str.encode("utf-8")
    future = CONFIG.QUARANTINE_PUBLISHER.publish(CONFIG.QUARANTINE_TOPIC_PATH, data, tx_id=tx_id, error=error)
    return future.result()


def quarantine_message(message: bytes, tx_id: str, error):
    logger.error("Quarantining message")
    future = CONFIG.QUARANTINE_PUBLISHER.publish(CONFIG.QUARANTINE_TOPIC_PATH, message, tx_id=tx_id, error=error)
    return future.result()
