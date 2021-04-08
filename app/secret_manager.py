from google.cloud import secretmanager
import structlog

logger = structlog.get_logger()


def get_secret(project_id, secret_id):
    """
    SDX's secrets are managed by Google Secret Manager.
    This method provides a way of retrieving a specific secret.

    The project id is passed as a parameter to allow for cases where the
    Secret Manager is not located in the same project as the service.
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
