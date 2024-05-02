import datetime

from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file("./service.json")

from google.cloud import storage

storage_client = storage.Client(credentials=credentials)
bucket_name = "reelsify-65e45.appspot.com"
bucket = storage_client.bucket(bucket_name)

def file_exists(name: str):
    return storage.Blob(bucket=bucket, name=name).exists(storage_client)

def generate_download_signed_url_v4(blob_name):
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        version="v4",
        # This URL is valid for 15 minutes
        expiration=datetime.timedelta(minutes=15),
        # Allow GET requests using this URL.
        method="GET",
    )
    return url

def upload_blob(source_file_name, destination_blob_name):
    blob = bucket.blob(destination_blob_name)

    generation_match_precondition = 0

    blob.upload_from_filename(source_file_name, if_generation_match=generation_match_precondition)

    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )