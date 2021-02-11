import structlog

from concurrent.futures import TimeoutError
from structlog.contextvars import bind_contextvars, clear_contextvars
from app import survey_subscriber, subscription_path
from app.collect import process
from app.errors import RetryableError
from app.quarantine import quarantine_submission, quarantine_message

logger = structlog.get_logger()


def callback(message):
    tx_id = None
    encrypted_message_str = None

    try:
        tx_id = message.attributes.get('tx_id')
        bind_contextvars(tx_id=tx_id)
        encrypted_message_str = message.data.decode('utf-8')
        process(encrypted_message_str)
        message.ack()
        clear_contextvars()

    except RetryableError as r:
        logger.info("retryable error, nacking message")
        logger.error(str(r))
        message.nack()
        clear_contextvars()

    except Exception as e:
        logger.info("quarantining message")
        logger.error(str(e))
        message.ack()
        if encrypted_message_str is None:
            logger.info("encrypted_message_str is none, quarantining message instead!")
            quarantine_message(message, tx_id)
        else:
            quarantine_submission(encrypted_message_str, tx_id)
        clear_contextvars()


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
