import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from .settings import settings

def _client():
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        config=Config(s3={"addressing_style": "path"})  # more convenient for LocalStack
    )

def ensure_bucket():
    s3 = _client()
    try:
        s3.head_bucket(Bucket=settings.S3_BUCKET)
    except ClientError:
        # Create bucket with proper LocationConstraint for eu-central-1
        if settings.AWS_REGION == "eu-central-1":
            s3.create_bucket(
                Bucket=settings.S3_BUCKET,
                CreateBucketConfiguration={"LocationConstraint": settings.AWS_REGION}
            )
        else:
            s3.create_bucket(Bucket=settings.S3_BUCKET)

def presigned_get_url(key: str, expires: int = 3600) -> str:
    s3 = _client()
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.S3_BUCKET, "Key": key},
        ExpiresIn=expires,
    )
    # to open link from the local environment:
    return url.replace("http://localstack:4566", settings.S3_PUBLIC_BASE)
