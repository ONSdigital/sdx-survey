import os
import logging
from google.cloud import pubsub_v1

LOGGING_LEVEL = logging.getLevelName(os.getenv('LOGGING_LEVEL', 'INFO'))
LOGGING_FORMAT = "%(asctime)s.%(msecs)06dZ|%(levelname)s: sdx-worker: %(message)s"

logging.basicConfig(
    format=LOGGING_FORMAT,
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=LOGGING_LEVEL,
)

PROJECT_ID = "ons-sdx-sandbox"

# publish config

dap_topic_id = "dap-topic"
receipt_topic_id = "receipt-topic"
quarantine_topic_id = "quarantine-topic"

dap_publisher = pubsub_v1.PublisherClient()
# The `topic_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/topics/{topic_id}`
dap_topic_path = dap_publisher.topic_path(PROJECT_ID, dap_topic_id)

receipt_publisher = pubsub_v1.PublisherClient()
receipt_topic_path = receipt_publisher.topic_path(PROJECT_ID, receipt_topic_id)

quarantine_publisher = pubsub_v1.PublisherClient()
quarantine_topic_path = quarantine_publisher.topic_path(PROJECT_ID, quarantine_topic_id)

# Subscriber config
subscription_id = "survey-subscription"

survey_subscriber = pubsub_v1.SubscriberClient()
# The `subscription_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/subscriptions/{subscription_id}`
subscription_path = survey_subscriber.subscription_path(PROJECT_ID, subscription_id)

# Config connecting to transform service
TRANSFORM_SERVICE_HOST = os.getenv('SDX_TRANSFORM_SERVICE_HOST', 'localhost')
TRANSFORM_SERVICE_PORT = os.getenv('SDX_TRANSFORM_SERVICE_PORT', 5002)
TRANSFORM_SERVICE_URL = f'{TRANSFORM_SERVICE_HOST}:{TRANSFORM_SERVICE_PORT}'

DELIVER_SERVICE_HOST = os.getenv('SDX_DELIVER_SERVICE_HOST', 'localhost')
DELIVER_SERVICE_PORT = os.getenv('SDX_DELIVER_SERVICE_PORT', 5001)
DELIVER_SERVICE_URL = f'{DELIVER_SERVICE_HOST}:{DELIVER_SERVICE_PORT}'
