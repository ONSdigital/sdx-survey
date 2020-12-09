from google.cloud import storage

bucket_name = "sdx-outputs"
# source_file_name = "/Users/tomholroyd/sdx-gcp/sdx-worker/app/test-data.txt"
directory = "surveys"


# bucket_name = "your-bucket-name"
# source_file_name = "local/path/to/file"
# path = "storage-object-name"


def upload_file(data, filename):
    """Uploads a string to the bucket."""
    path = f"{directory}/{filename}"
    storage_client = storage.Client("ons-sdx-sandbox")
    bucket = storage_client.bucket('sdx-outputs')
    blob = bucket.blob(path)

    blob.upload_from_string(data)
    # blob.upload_from_filename(source_file_name)

    print('Successfully uploaded: ', filename)
