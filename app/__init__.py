import os
from google.cloud import pubsub_v1, storage
from google.cloud import datastore
from app.logger import logging_config
from app.secret_manager import get_secret_list
from app.decrypt import add_keys


logging_config()

project_id = os.getenv('PROJECT_ID', 'ons-sdx-sandbox')
receipt_topic_path = os.getenv('RECEIPT_TOPIC_PATH', 'projects/ons-sdx-sandbox/topics/receipt-topic')
srm_receipt_topic_path = os.getenv('SRM_RECEIPT_TOPIC_PATH', 'projects/ons-sdx-sandbox/topics/srm-receipt-topic')
subscription_id = "survey-trigger-subscription"
quarantine_topic_id = "quarantine-survey-topic"
transform_service_url = "sdx-transform:80"
deliver_service_url = "sdx-deliver:80"


class Config:
    """Class to hold required configuration data"""

    def __init__(self, proj_id) -> None:
        self.PROJECT_ID = proj_id
        self.TRANSFORM_SERVICE_URL = transform_service_url
        self.DELIVER_SERVICE_URL = deliver_service_url
        self.ENCRYPT_COMMENT_KEY = None
        self.SURVEY_SUBSCRIBER = None
        self.SURVEY_SUBSCRIPTION_PATH = None
        self.RECEIPT_PUBLISHER = None
        self.RECEIPT_TOPIC_PATH = receipt_topic_path
        self.SRM_RECEIPT_TOPIC_PATH = srm_receipt_topic_path
        self.QUARANTINE_PUBLISHER = None
        self.QUARANTINE_TOPIC_PATH = None
        self.DATASTORE_CLIENT = None
        self.BUCKET_NAME = f'{proj_id}-survey-responses'
        self.BUCKET = None


CONFIG = Config(project_id)


def cloud_config():
    """
    Loads configuration required for running against GCP based environments

    This function makes calls to GCP native tools such as Google Secret Manager
    and therefore should not be called in situations where these connections are
    not possible, e.g running the unit tests locally.
    """

    storage_client = storage.Client(CONFIG.PROJECT_ID)
    CONFIG.BUCKET = storage_client.bucket(CONFIG.BUCKET_NAME)

    add_keys(get_secret_list(project_id, 'sdx-private-jwt'))
    add_keys(get_secret_list(project_id, 'eq-public-signing'))
    add_keys(get_secret_list(project_id, 'eq-public-jws'))

    CONFIG.ENCRYPT_COMMENT_KEY = get_secret_list(project_id, 'sdx-comment-key')[0]

    survey_subscriber = pubsub_v1.SubscriberClient()
    CONFIG.SURVEY_SUBSCRIPTION_PATH = survey_subscriber.subscription_path(project_id, subscription_id)
    CONFIG.SURVEY_SUBSCRIBER = survey_subscriber

    CONFIG.RECEIPT_PUBLISHER = pubsub_v1.PublisherClient()

    quarantine_publisher = pubsub_v1.PublisherClient()
    CONFIG.QUARANTINE_TOPIC_PATH = quarantine_publisher.topic_path(project_id, quarantine_topic_id)
    CONFIG.QUARANTINE_PUBLISHER = quarantine_publisher

    CONFIG.DATASTORE_CLIENT = datastore.Client(project=project_id)
