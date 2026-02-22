import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "S3バケットが存在しなければ作成する"

    def handle(self, **options: object) -> None:  # noqa: ARG002
        client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
        )
        bucket: str = settings.S3_BUCKET_NAME
        try:
            client.head_bucket(Bucket=bucket)
            self.stdout.write(f"Bucket '{bucket}' already exists.")
        except ClientError:
            client.create_bucket(Bucket=bucket)
            self.stdout.write(
                self.style.SUCCESS(f"Bucket '{bucket}' created.")
            )
