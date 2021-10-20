from google.cloud import secretmanager
import structlog

logger = structlog.get_logger()


def get_secret(project_id, secret_id) -> list:
    """
    Secrets are managed by Google Secret Manager.

    This method returns a list of the currently enabled versions
    of the secret with name "secret_id" in the given project.
    """

    logger.info(f"Checking for versions of {secret_id}")
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    parent = client.secret_path(project_id, secret_id)

    secrets = []
    for version in client.list_secret_versions(request={"parent": parent}):
        if version.state.name == "ENABLED":
            logger.info(f"Getting secret { version.name} from Secret Manager")
            response = client.access_secret_version(request={"name": version.name})
            secrets.append(response.payload.data.decode("UTF-8"))

    if len(secrets) < 1:
        logger.error(f"No enabled versions of {secret_id}")

    return secrets
