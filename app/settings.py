from typing import Annotated

from sdx_base.settings.app import AppSettings, get_settings
from sdx_base.settings.service import SECRET


class Settings(AppSettings):
    receipt_topic_path: str = 'projects/ons-sdx-sandbox/topics/receipt-topic'
    srm_receipt_topic_path: str = 'projects/ons-sdx-sandbox/topics/srm-receipt-topic'
    subscription_id: str = "survey-trigger-subscription"
    quarantine_topic_id: str = "quarantine-survey-topic"
    deliver_service_url: str = "http://sdx-deliver:80"
    image_service_url: str = "http://sdx-image:80"
    transformer_service_url: str = "http://sdx-transformer:80"
    sdx_private_jwt: Annotated[SECRET, "sdx-private-jwt"]
    eq_public_signing: Annotated[SECRET, "eq-public-signing"]
    eq_public_jws: Annotated[SECRET, "eq-public-jws"]
    sdx_comment_key: Annotated[SECRET, "sdx-comment-key"]
    ftp_path: Annotated[SECRET, "ftp-path"]

    def get_bucket_name(self) -> str:
        return f'{self.project_id}-survey-responses'


def get_instance() -> Settings:
    return get_settings(Settings)