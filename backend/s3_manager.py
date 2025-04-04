# s3_manager.py
import os
from dotenv import load_dotenv
import boto3
import tempfile

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)


def list_pdfs():
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME)
    return [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.pdf')]

def download_pdf_from_s3(pdf_key: str) -> str:
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    s3_client.download_fileobj(S3_BUCKET_NAME, pdf_key, temp_file)
    temp_file.close()
    return temp_file.name
