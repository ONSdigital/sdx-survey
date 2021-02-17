from app import quarantine_publisher, quarantine_topic_path


def quarantine_submission(data_str: str, tx_id: str, error):
    data = data_str.encode("utf-8")
    future = quarantine_publisher.publish(quarantine_topic_path, data, tx_id=tx_id, error=error)
    return future.result()


def quarantine_message(message: bytes, tx_id: str, error):
    future = quarantine_publisher.publish(quarantine_topic_path, message, tx_id=tx_id, error=error)
    return future.result()
