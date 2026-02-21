import datetime
from typing import Any

import pytest
from rest_framework.test import APIClient

from books.models import Author
from books.models import Book


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
