from concurrent.futures import TimeoutError
from app import subscriber, subscription_path

from app.collect import process


def callback(message):
    process(message)
    message.ack()


def start():

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}..\n")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with subscriber:
        try:
            # When `timeout` is not set, result() will block indefinitely,
            # unless an exception is encountered first.
            streaming_pull_future.result()
        except TimeoutError:
            streaming_pull_future.cancel()
