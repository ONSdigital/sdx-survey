import os
from google.cloud import pubsub_v1
from google.cloud import datastore
from app.logger import logging_config
from app.secret_manager import get_secret


logging_config()

PROJECT_ID = os.getenv('PROJECT_ID', 'ons-sdx-tom')

# connections
TRANSFORM_SERVICE_URL = "sdx-transform:80"
DELIVER_SERVICE_URL = "sdx-deliver:80"

# pubsub config
dap_topic_id = "dap-topic"
receipt_topic_id = "receipt-topic"
quarantine_topic_id = "quarantine-topic"
subscription_id = "survey-subscription"

dap_publisher = None
dap_topic_path = None

receipt_publisher = None
receipt_topic_path = None

quarantine_publisher = None
quarantine_topic_path = None

survey_subscriber = None
subscription_path = None

# keys
DECRYPT_SURVEY_KEY = None
ENCRYPT_COMMENT_KEY = None

datastore_client = None


def load_config():

    global DECRYPT_SURVEY_KEY
    DECRYPT_SURVEY_KEY = get_secret(PROJECT_ID, 'sdx-worker-decrypt')
    global ENCRYPT_COMMENT_KEY
    ENCRYPT_COMMENT_KEY = get_secret(PROJECT_ID, 'sdx-comment-key')

    global dap_publisher
    dap_publisher = pubsub_v1.PublisherClient()
    global dap_topic_path
    dap_topic_path = dap_publisher.topic_path(PROJECT_ID, dap_topic_id)

    global receipt_publisher
    receipt_publisher = pubsub_v1.PublisherClient()
    global receipt_topic_path
    receipt_topic_path = receipt_publisher.topic_path(PROJECT_ID, receipt_topic_id)

    global quarantine_publisher
    quarantine_publisher = pubsub_v1.PublisherClient()

    global quarantine_topic_path
    quarantine_topic_path = quarantine_publisher.topic_path(PROJECT_ID, quarantine_topic_id)

    global survey_subscriber
    survey_subscriber = pubsub_v1.SubscriberClient()
    global subscription_path
    subscription_path = survey_subscriber.subscription_path(PROJECT_ID, subscription_id)

    global datastore_client
    datastore_client = datastore.Client(project=PROJECT_ID)
