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
    """
    Manages the life cycle of the received message.

    Handles pre processing events such as setting up logging bindings.
    Extracts the data and passes it on to be processed.
    Handles post processing events such acking the message and
    catching exceptions raised during processing.
    """

    encrypted_message_str = None
    tx_id = message.attributes.get('tx_id')
    bind_contextvars(app="SDX-Survey")
    bind_contextvars(tx_id=tx_id)
    bind_contextvars(thread=threading.currentThread().getName())

    try:
        encrypted_message_str = message.data.decode('utf-8')
        process(message)
        message.ack()

    except RetryableError as r:
        logger.error("Retryable error, nacking message", error=str(r))
        message.nack()

    except Exception as error:
        if encrypted_message_str is None:
            logger.error("encrypted_message_str is none, quarantining message instead!")
            quarantine_message(message, tx_id, str(error))
        else:
            logger.error(f"quarantining message: {error}")
            quarantine_submission(encrypted_message_str, tx_id, str(error))
        message.ack()

    finally:
        clear_contextvars()


def start():
    """
    Begin listening to the survey pubsub subscription.

    This functions spawns new threads that listen to the subscription topic and
    on receipt of a message invoke the callback function

    The main thread blocks indefinitely unless the connection times out

    """

    streaming_pull_future = CONFIG.SURVEY_SUBSCRIBER.subscribe(CONFIG.SURVEY_SUBSCRIPTION_PATH, callback=callback)
    logger.info(f"Listening for messages on {CONFIG.SURVEY_SUBSCRIPTION_PATH}..\n")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with CONFIG.SURVEY_SUBSCRIBER:
        try:
            # Result() will block indefinitely, unless an exception is encountered first.
            streaming_pull_future.result()
        except TimeoutError as te:
            logger.error("TimeoutError error, stopping listening", error=str(te))
            streaming_pull_future.cancel()
