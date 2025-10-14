from fastapi import Depends
from sdx_base.services.datastore import DatastoreService
from sdx_base.services.http import HttpService
from sdx_base.services.pubsub import PubsubService
from sdx_base.services.storage import StorageService

from app.definitions.comments import CommentsBase
from app.definitions.decrypter import DecryptionBase
from app.definitions.deliver import DeliverBase
from app.definitions.http import TransformPosterBase, ImagePosterBase
from app.definitions.processor import ProcessorBase
from app.definitions.receipting import ReceiptServiceBase
from app.definitions.transformer import TransformerBase
from app.services.comments import CommentsService
from app.services.decrypter import DecryptionService
from app.services.deliver import DeliverService
from app.services.processor import SurveyProcessorV2, AdhocProcessorV2, FeedbackProcessorV2
from app.services.receipt import ReceiptService
from app.services.transformer import TransformService
from app.settings import Settings, get_instance
from app.survey import BucketReader, Survey
from app.transformation.image_poster import ImagePoster
from app.transformation.selector import TransformSelector
from app.transformation.transformer_poster import TransformPoster


def get_settings() -> Settings:
    return get_instance()


def get_datastore_service() -> DatastoreService:
    return DatastoreService()


def get_http_service() -> HttpService:
    return HttpService()


def get_pubsub_service() -> PubsubService:
    return PubsubService()


def get_storage_service() -> StorageService:
    return StorageService()


def get_comments_service(settings: Settings = Depends(get_settings),
                         datastore: DatastoreService = Depends(get_datastore_service)) -> CommentsService:
    return CommentsService(settings, datastore)


def get_decryption_service(settings: Settings = Depends(get_settings)) -> DecryptionService:
    return DecryptionService(settings)


def get_deliver_service(settings: Settings = Depends(get_settings),
                        http: HttpService = Depends(get_http_service)) -> DeliverService:
    return DeliverService(settings.deliver_service_url, http)


def get_receipt_service(settings: Settings = Depends(get_settings),
                        publish: PubsubService = Depends(get_pubsub_service)) -> ReceiptService:
    return ReceiptService(settings, publish)


def get_transform_poster(settings: Settings = Depends(get_settings),
                        http_service: HttpService = Depends(get_http_service)) -> TransformPoster:
    return TransformPoster(transformer_url=settings.transformer_service_url, http_service=http_service)


def get_image_poster(settings: Settings = Depends(get_settings),
                     http_service: HttpService = Depends(get_http_service)) -> ImagePoster:
    return ImagePoster(image_url=settings.image_service_url, http_service=http_service)


def get_transform_selector(transform_poster: TransformPosterBase = Depends(get_transform_poster),
                           image_poster: ImagePosterBase = Depends(get_image_poster),
                           settings: Settings = Depends(get_settings)) -> TransformSelector:
    return TransformSelector(transform_poster=transform_poster, image_poster=image_poster, ftp_path=settings.ftp_path)


def get_transformer_service(
    transform_selector: TransformSelector = Depends(get_transform_selector)
) -> TransformService:
    return TransformService(transform_selector)


def get_survey_processor(transformer_service: TransformerBase = Depends(get_transformer_service),
                         deliver_service: DeliverBase = Depends(get_deliver_service),
                         receipt_service: ReceiptServiceBase = Depends(get_receipt_service),
                         comments_service: CommentsBase = Depends(get_comments_service)) -> SurveyProcessorV2:
    return SurveyProcessorV2(transformer_service, deliver_service, receipt_service, comments_service)


def get_adhoc_processor(transformer_service: TransformerBase = Depends(get_transformer_service),
                        deliver_service: DeliverBase = Depends(get_deliver_service),
                        receipt_service: ReceiptServiceBase = Depends(get_receipt_service),
                        comments_service: CommentsBase = Depends(get_comments_service)) -> AdhocProcessorV2:
    return AdhocProcessorV2(transformer_service, deliver_service, receipt_service, comments_service)


def get_feedback_processor(transformer_service: TransformerBase = Depends(get_transformer_service),
                           deliver_service: DeliverBase = Depends(get_deliver_service),
                           receipt_service: ReceiptServiceBase = Depends(get_receipt_service),
                           comments_service: CommentsBase = Depends(get_comments_service)) -> FeedbackProcessorV2:
    return FeedbackProcessorV2(transformer_service, deliver_service, receipt_service, comments_service)


def get_survey(settings: Settings = Depends(get_settings),
                 bucket_reader: BucketReader = Depends(get_storage_service),
                 decryption_service: DecryptionBase = Depends(get_decryption_service),
                 survey_processor: ProcessorBase = Depends(get_survey_processor),
                 adhoc_processor: ProcessorBase = Depends(get_adhoc_processor),
                 feedback_processor: ProcessorBase = Depends(get_feedback_processor)) -> Survey:
    return Survey(settings,
                  bucket_reader=bucket_reader,
                  decryption_service=decryption_service,
                  survey_processor=survey_processor,
                  adhoc_processor=adhoc_processor,
                  feedback_processor=feedback_processor)
