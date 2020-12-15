from app import quarantine_publisher, quarantine_topic_path


def quarantine_submission(data_str: str, tx_id: str):
    # Data must be a bytestring
    data = data_str.encode("utf-8")
    # When you publish a message, the client returns a future.
    future = quarantine_publisher.publish(quarantine_topic_path, data, tx_id=tx_id)
    return future.result()
