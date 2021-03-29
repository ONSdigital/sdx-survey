from google.cloud import secretmanager
import structlog

logger = structlog.get_logger()


def get_secret(project_id, secret_id):
    """
    This

    :param project_id:
    :param secret_id:
    :return: Secret stored in GCP
    """
    version_id = 'latest'

    logger.info("Getting secrets from Secret Manager")
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    response = client.access_secret_version(request={"name": name})

    payload = response.payload.data.decode("UTF-8")
    return payload
