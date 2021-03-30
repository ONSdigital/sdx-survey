import threading
import structlog

from concurrent.futures import TimeoutError
from structlog.contextvars import bind_contextvars, clear_contextvars
from app import CONFIG
from app.collect import process
from app.errors import RetryableError
from app.quarantine import quarantine_submission, quarantine_message
logger = structlog.get_logger()


def callback(message):
    tx_id = None
    encrypted_message_str = None

    try:
        tx_id = message.attributes.get('tx_id')
        bind_contextvars(app="SDX-Survey")
        bind_contextvars(tx_id=tx_id)
        bind_contextvars(thread=threading.currentThread().getName().split('_')[1])
        encrypted_message_str = message.data.decode('utf-8')
        process(encrypted_message_str)
        message.ack()

    except RetryableError as r:
        logger.error("Retryable error, nacking message", error=str(r))
        message.nack()

    except Exception as error:
        message.ack()
        if encrypted_message_str is None:
            logger.info("encrypted_message_str is none, quarantining message instead!")
            quarantine_message(message, tx_id, str(error))
        else:
            quarantine_submission(encrypted_message_str, tx_id, str(error))
    finally:
        clear_contextvars()


def start():
    streaming_pull_future = CONFIG.SURVEY_SUBSCRIBER.subscribe(CONFIG.SURVEY_SUBSCRIPTION_PATH, callback=callback)
    logger.info(f"Listening for messages on {CONFIG.SURVEY_SUBSCRIPTION_PATH}..\n")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with CONFIG.SURVEY_SUBSCRIBER:
        try:
            # Result() will block indefinitely, unless an exception is encountered first.
            streaming_pull_future.result()
        except TimeoutError:
            streaming_pull_future.cancel()
