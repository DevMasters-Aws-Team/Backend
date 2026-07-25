import boto3
from src.config import settings

def get_boto3_client(service_name: str):
    """Returns a boto3 client configured for the specified AWS region."""
    return boto3.client(
        service_name,
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
