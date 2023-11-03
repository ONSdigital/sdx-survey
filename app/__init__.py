import os

from sdx_gcp.app import SdxApp

from app.decrypt import add_keys

project_id = os.getenv('PROJECT_ID', 'ons-sdx-sandbox')
receipt_topic_path = os.getenv('RECEIPT_TOPIC_PATH', 'projects/ons-sdx-sandbox/topics/receipt-topic')
srm_receipt_topic_path = os.getenv('SRM_RECEIPT_TOPIC_PATH', 'projects/ons-sdx-sandbox/topics/srm-receipt-topic')
subscription_id = "survey-trigger-subscription"
quarantine_topic_id = "quarantine-survey-topic"
transform_service_url = os.getenv('TRANSFORM_SERVICE_URL', "http://sdx-transform:80")
deliver_service_url = os.getenv("DELIVER_SERVICE_URL", "http://sdx-deliver:80")
survey_responses_bucket = f'{project_id}-survey-responses'
image_service_url = os.getenv('IMAGE_SERVICE_URL', "http://sdx-image:80")
transformer_service_url = os.getenv('TRANSFORMER_SERVICE_URL', "transformer-url")


class Config:
    """Class to hold required configuration data"""

    def __init__(self, proj_id) -> None:
        self.PROJECT_ID = proj_id
        self.TRANSFORM_SERVICE_URL = transform_service_url
        self.DELIVER_SERVICE_URL = deliver_service_url
        self.ENCRYPT_COMMENT_KEY = None
        self.RECEIPT_TOPIC_PATH = receipt_topic_path
        self.SRM_RECEIPT_TOPIC_PATH = srm_receipt_topic_path
        self.QUARANTINE_TOPIC_ID = quarantine_topic_id
        self.BUCKET_NAME = survey_responses_bucket
        self.FTP_PATH = None
        self.IMAGE_SERVICE_URL = image_service_url
        self.TRANSFORM_SERVICE_URL = transformer_service_url


CONFIG = Config(project_id)

sdx_app = SdxApp("sdx-survey", project_id)


def setup_keys():
    add_keys(sdx_app.secrets_get('sdx-private-jwt'))
    add_keys(sdx_app.secrets_get('eq-public-signing'))
    add_keys(sdx_app.secrets_get('eq-public-jws'))
    CONFIG.FTP_PATH = sdx_app.secrets_get("ftp-path")[0]
    CONFIG.ENCRYPT_COMMENT_KEY = sdx_app.secrets_get('sdx-comment-key')[0]
