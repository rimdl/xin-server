import boto3
import os


S3_URL = os.environ.get('S3_URL')
S3_BUCKET = os.environ.get('S3_BUCKET')
S3_KEYID = os.environ.get('S3_KEYID')
S3_KEY = os.environ.get('S3_KEY')

s3_client = boto3.client(
    's3',
    aws_access_key_id=S3_KEYID,
    aws_secret_access_key=S3_KEY,
    endpoint_url=S3_URL,
)

bucket_name = S3_BUCKET


def upload(file, key):
    try:
        s3_client.upload_fileobj(file, bucket_name, key)
        s3_client.close()
        print("file uploaded")
        return f"{bucket_name}/{key}"
    except Exception as e:
        print(f"Error occurred: {e}")
        return False
