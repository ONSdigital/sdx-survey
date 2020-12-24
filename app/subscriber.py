import logging
from concurrent.futures import TimeoutError

from structlog import wrap_logger

from app import survey_subscriber, subscription_path
from app.collect import process
from app.errors import RetryableError

logger = wrap_logger(logging.getLogger(__name__))


def callback(message):
    try:
        encrypted_message_str = message.data.decode('utf-8')
        process(encrypted_message_str)
        message.ack()
    except RetryableError:
        logger.info("retryable error, nacking message")
        message.nack()
    except Exception as e:
        logger.error(f"error {str(e)}, nacking message")
        message.nack()


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
