import os
from google.cloud import pubsub_v1
from google.cloud import datastore
from app.logger import logging_config
from app.secret_manager import get_secret


logging_config()

project_id = os.getenv('PROJECT_ID', 'ons-sdx-sandbox')
subscription_id = "survey-subscription"
receipt_topic_id = "receipt-topic"
quarantine_topic_id = "quarantine-survey-topic"


class Config:

    def __init__(self, proj_id) -> None:
        self.PROJECT_ID = proj_id
        self.TRANSFORM_SERVICE_URL = "sdx-transform:80"
        self.DELIVER_SERVICE_URL = "sdx-deliver:80"
        self.DECRYPT_SURVEY_KEY = None
        self.ENCRYPT_COMMENT_KEY = "E3rjFT2i9ALcvc99Pe3YqjIGrzm3LdMsCXc8nUaOEbc="
        self.SURVEY_SUBSCRIBER = None
        self.SURVEY_SUBSCRIPTION_PATH = None
        self.RECEIPT_PUBLISHER = None
        self.RECEIPT_TOPIC_PATH = None
        self.QUARANTINE_PUBLISHER = None
        self.QUARANTINE_TOPIC_PATH = None
        self.DATASTORE_CLIENT = None


CONFIG = Config(project_id)


def cloud_config():
    """
    The cloud_config method gives us a way of unit-testing various parts of our code without making GCP Connections.
    Thus preventing various errors when GitHub actions runs all tests. For example: Permission Denied error
    """

    CONFIG.DECRYPT_SURVEY_KEY = get_secret(project_id, 'sdx-private-jwt')
    CONFIG.AUTHENTICATE_SURVEY_KEY = get_secret(project_id, 'eq-public-signing')
    CONFIG.ENCRYPT_COMMENT_KEY = get_secret(project_id, 'sdx-comment-key')

    survey_subscriber = pubsub_v1.SubscriberClient()
    CONFIG.SURVEY_SUBSCRIPTION_PATH = survey_subscriber.subscription_path(project_id, subscription_id)
    CONFIG.SURVEY_SUBSCRIBER = survey_subscriber

    receipt_publisher = pubsub_v1.PublisherClient()
    CONFIG.RECEIPT_TOPIC_PATH = receipt_publisher.topic_path(project_id, receipt_topic_id)
    CONFIG.RECEIPT_PUBLISHER = receipt_publisher

    quarantine_publisher = pubsub_v1.PublisherClient()
    CONFIG.QUARANTINE_TOPIC_PATH = quarantine_publisher.topic_path(project_id, quarantine_topic_id)
    CONFIG.QUARANTINE_PUBLISHER = quarantine_publisher

    CONFIG.DATASTORE_CLIENT = datastore.Client(project=project_id)
