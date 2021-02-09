import logging
from concurrent.futures import TimeoutError

from structlog import wrap_logger

from app import survey_subscriber, subscription_path
from app.collect import process
from app.errors import RetryableError
from app.quarantine import quarantine_submission, quarantine_message

logger = wrap_logger(logging.getLogger(__name__))


def callback(message):
    tx_id = None
    encrypted_message_str = None

    try:
        tx_id = message.attributes.get('tx_id')
        encrypted_message_str = message.data.decode('utf-8')
        process(encrypted_message_str)
        message.ack()

    except RetryableError as r:
        logger.info("retryable error, nacking message")
        logger.error(str(r))
        message.nack()

    except Exception as e:
        logger.info("quarantining message")
        logger.error(str(e))
        message.ack()
        if encrypted_message_str is None:
            logger.info("encrypted_message_str is none, quarantining message instead!")
            quarantine_message(message, tx_id)
        else:
            quarantine_submission(encrypted_message_str, tx_id)


def start():

    streaming_pull_future = survey_subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}..\n")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with survey_subscriber:
        try:
            # Result() will block indefinitely, unless an exception is encountered first.
            streaming_pull_future.result()
        except TimeoutError:
            streaming_pull_future.cancel()
