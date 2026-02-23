"""機能テスト用フィクスチャ.

API エンドポイントテストで使用する共通フィクスチャを定義する.
"""

import datetime
from collections.abc import Generator
from io import BytesIO
from typing import Any

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient

from authors.models import Author
from books.entities import Book
from notifications.infrastructure.adapters.fake import FakeNotifier
from notifications.infrastructure.containers.notificaton import (
    NotificationModule,
)
from notifications.infrastructure.containers.notificaton import container


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def author(db: Any) -> Author:
    return Author.objects.create(name="夏目漱石", bio="日本の小説家")


@pytest.fixture
def book(author: Author) -> Book:
    return Book.objects.create(
        title="吾輩は猫である",
        isbn="9784003101018",
        published_date=datetime.date(1905, 1, 1),
        author=author,
    )


@pytest.fixture(autouse=True)
def _memory_storage(settings: Any) -> None:
    """テスト用にインメモリストレージを使用する."""
    settings.STORAGES = {
        "default": {
            "BACKEND": ("django.core.files.storage.InMemoryStorage"),
        },
        "staticfiles": {
            "BACKEND": (
                "django.contrib.staticfiles.storage.StaticFilesStorage"
            ),
        },
    }


@pytest.fixture
def fake_notifier() -> Generator[FakeNotifier]:
    """テスト用の FakeNotifier を DI に差し込む."""
    notifier = FakeNotifier()
    container.override(
        NotificationModule(notifier_override=notifier),
    )
    yield notifier
    container.reset()


@pytest.fixture
def test_image() -> SimpleUploadedFile:
    """テスト用の最小画像ファイルを生成する."""
    buf = BytesIO()
    img = Image.new("RGB", (100, 100), color="red")
    img.save(buf, format="PNG")
    buf.seek(0)
    return SimpleUploadedFile(
        name="test.png",
        content=buf.read(),
        content_type="image/png",
    )
