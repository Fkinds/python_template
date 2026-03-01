from typing import Any

import boto3
import pytest
from django.core.management import call_command
from moto import mock_aws


@pytest.fixture
def s3_mock(settings: Any) -> Any:
    """moto で S3 をモックする."""
    with mock_aws() as m:
        settings.S3_ENDPOINT_URL = None
        settings.S3_ACCESS_KEY = "testing"
        settings.S3_SECRET_KEY = "testing"
        settings.S3_BUCKET_NAME = "test-media"
        yield m


class TestEnsureBucket:
    def test_happy_creates_bucket_when_missing(
        self,
        s3_mock: Any,
        settings: Any,
    ) -> None:
        """バケットが存在しない場合に作成されること."""
        # Act
        call_command("ensure_bucket")

        # Assert
        client = boto3.client(
            "s3",
            region_name="us-east-1",
            aws_access_key_id="testing",
            aws_secret_access_key="testing",
        )
        buckets = client.list_buckets()["Buckets"]
        names = [b["Name"] for b in buckets]
        assert settings.S3_BUCKET_NAME in names

    def test_happy_skips_when_bucket_exists(
        self,
        s3_mock: Any,
        settings: Any,
    ) -> None:
        """バケットが既に存在する場合はスキップすること."""
        from django.core.management import call_command

        # Arrange
        client = boto3.client(
            "s3",
            region_name="us-east-1",
            aws_access_key_id="testing",
            aws_secret_access_key="testing",
        )
        client.create_bucket(
            Bucket=settings.S3_BUCKET_NAME,
        )

        # Act — 再実行してもエラーにならない
        call_command("ensure_bucket")

        # Assert
        buckets = client.list_buckets()["Buckets"]
        names = [b["Name"] for b in buckets]
        assert names.count(settings.S3_BUCKET_NAME) == 1
