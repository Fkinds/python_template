from typing import Any

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from hypothesis import given
from hypothesis import strategies as st
from rest_framework import status
from rest_framework.test import APIClient

from authors.models import Author
from books.entities import Book
from notifications.infrastructure.adapters.fake import FakeNotifier
from notifications.infrastructure.containers.notificaton import (
    NotificationModule,
)
from notifications.infrastructure.containers.notificaton import container


@pytest.mark.django_db
class TestBookListCreate:
    endpoint = "/api/books/"

    # --- 正常系 ---

    def test_happy_list_returns_zero_count_when_empty(
        self, api_client: APIClient, db: Any
    ) -> None:
        # Act
        response = api_client.get(self.endpoint)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

    def test_happy_list_returns_nested_author(
        self, api_client: APIClient, book: Book
    ) -> None:
        # Act
        response = api_client.get(self.endpoint)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        result = response.data["results"][0]
        assert isinstance(result["author"], dict)
        assert "name" in result["author"]

    def test_happy_create_book(
        self,
        api_client: APIClient,
        author: Author,
        fake_notifier: FakeNotifier,
    ) -> None:
        # Arrange
        payload = {
            "title": "坊っちゃん",
            "isbn": "9784003101025",
            "published_date": "1906-04-01",
            "author": author.pk,
        }

        # Act
        response = api_client.post(self.endpoint, payload, format="json")

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert Book.objects.count() == 1
        assert response.data["title"] == "坊っちゃん"

    def test_happy_create_sends_notification(
        self,
        api_client: APIClient,
        author: Author,
        fake_notifier: FakeNotifier,
    ) -> None:
        """本の作成時に通知が送信されること."""
        # Arrange
        payload = {
            "title": "坊っちゃん",
            "isbn": "9784003101025",
            "published_date": "1906-04-01",
            "author": author.pk,
        }

        # Act
        api_client.post(self.endpoint, payload, format="json")

        # Assert
        assert len(fake_notifier.messages) == 1
        (msg,) = fake_notifier.messages
        assert "坊っちゃん" in msg
        assert "夏目漱石" in msg

    def test_happy_create_succeeds_despite_notification_failure(
        self,
        api_client: APIClient,
        author: Author,
    ) -> None:
        """通知送信失敗時でも本の作成は成功すること."""

        # Arrange
        class _FailingNotifier:
            def send(self, message: str) -> None:
                msg = "Discord 障害"
                raise RuntimeError(msg)

        container.override(
            NotificationModule(
                notifier_override=_FailingNotifier(),
            ),
        )
        payload = {
            "title": "坊っちゃん",
            "isbn": "9784003101025",
            "published_date": "1906-04-01",
            "author": author.pk,
        }

        # Act
        response = api_client.post(
            self.endpoint,
            payload,
            format="json",
        )

        # Assert
        assert response.status_code == (status.HTTP_201_CREATED)
        assert Book.objects.count() == 1

        # Cleanup
        container.reset()

    @given(
        title=st.text(
            min_size=1,
            max_size=255,
            alphabet=st.characters(
                whitelist_categories=("L", "N", "Zs"),
                whitelist_characters=(
                    "\u3000-\u303f\u30fc\u30fb"
                    "\u3001\u3002\uff01\uff1f"
                    "-,.!?'\"()&+:;/ \t"
                ),
            ),
        ).filter(lambda s: s.strip())
    )
    def test_happy_create_accepts_any_valid_title(self, title: str) -> None:
        # Arrange
        Book.objects.all().delete()
        Author.objects.all().delete()
        client = APIClient()
        author = Author.objects.create(name="テスト著者")
        payload = {
            "title": title,
            "isbn": "9784003101018",
            "published_date": "2000-01-01",
            "author": author.pk,
        }

        # Act
        response = client.post(self.endpoint, payload, format="json")

        # Assert
        assert response.status_code == status.HTTP_201_CREATED

    def test_happy_create_book_with_cover_image(
        self,
        api_client: APIClient,
        author: Author,
        test_image: SimpleUploadedFile,
    ) -> None:
        """カバー画像付きで本を作成できること."""
        # Arrange
        payload = {
            "title": "坊っちゃん",
            "isbn": "9784003101032",
            "published_date": "1906-04-01",
            "author": author.pk,
            "cover_image": test_image,
        }

        # Act
        response = api_client.post(
            self.endpoint,
            payload,
            format="multipart",
        )

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["cover_image"]

    def test_happy_create_book_without_cover_image(
        self,
        api_client: APIClient,
        author: Author,
    ) -> None:
        """カバー画像なしでも本を作成できること."""
        # Arrange
        payload = {
            "title": "三四郎",
            "isbn": "9784003101049",
            "published_date": "1908-01-01",
            "author": author.pk,
        }

        # Act
        response = api_client.post(
            self.endpoint,
            payload,
            format="json",
        )

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert not response.data["cover_image"]

    # --- 異常系 ---

    @pytest.mark.parametrize(
        "title",
        [
            "テスト😀",
            "<script>alert('xss')</script>",
        ],
        ids=["emoji", "script_tag"],
    )
    def test_error_create_rejects_unsafe_title(
        self,
        api_client: APIClient,
        author: Author,
        title: str,
    ) -> None:
        """異常系: 不正文字を含むタイトルが拒否されること."""
        # Arrange
        payload = {
            "title": title,
            "isbn": "9784003101025",
            "published_date": "2000-01-01",
            "author": author.pk,
        }

        # Act
        response = api_client.post(self.endpoint, payload, format="json")

        # Assert
        assert response.status_code == (status.HTTP_400_BAD_REQUEST)
        assert "title" in response.data

    def test_error_create_rejects_empty_body(
        self, api_client: APIClient, db: Any
    ) -> None:
        # Arrange
        payload: dict[str, str] = {}

        # Act
        response = api_client.post(self.endpoint, payload, format="json")

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        missing = {"title", "isbn", "published_date", "author"}
        assert missing <= set(response.data.keys())

    @pytest.mark.parametrize(
        ("missing_field", "payload_without"),
        [
            (
                "title",
                {
                    "isbn": "9784003101025",
                    "published_date": "1906-04-01",
                },
            ),
            (
                "isbn",
                {
                    "title": "テスト",
                    "published_date": "1906-04-01",
                },
            ),
        ],
        ids=["title", "isbn"],
    )
    def test_error_create_rejects_missing_field(
        self,
        api_client: APIClient,
        author: Author,
        missing_field: str,
        payload_without: dict[str, str],
    ) -> None:
        """異常系: 必須フィールドが欠けている場合に拒否されること."""
        # Arrange
        payload = {
            **payload_without,
            "author": author.pk,
        }

        # Act
        response = api_client.post(self.endpoint, payload, format="json")

        # Assert
        assert response.status_code == (status.HTTP_400_BAD_REQUEST)
        assert missing_field in response.data

    def test_error_create_rejects_duplicate_isbn(
        self, api_client: APIClient, book: Book
    ) -> None:
        # Arrange
        payload = {
            "title": "重複テスト",
            "isbn": book.isbn,
            "published_date": "2000-01-01",
            "author": book.author.pk,
        }

        # Act
        response = api_client.post(self.endpoint, payload, format="json")

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "isbn" in response.data

    def test_error_create_rejects_isbn_too_long(
        self, api_client: APIClient, author: Author
    ) -> None:
        # Arrange
        payload = {
            "title": "テスト",
            "isbn": "12345678901234",
            "published_date": "2000-01-01",
            "author": author.pk,
        }

        # Act
        response = api_client.post(self.endpoint, payload, format="json")

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "isbn" in response.data

    def test_error_create_rejects_invalid_date(
        self, api_client: APIClient, author: Author
    ) -> None:
        # Arrange
        payload = {
            "title": "テスト",
            "isbn": "1234567890123",
            "published_date": "not-a-date",
            "author": author.pk,
        }

        # Act
        response = api_client.post(self.endpoint, payload, format="json")

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "published_date" in response.data

    def test_error_create_rejects_nonexistent_author(
        self, api_client: APIClient, db: Any
    ) -> None:
        # Arrange
        payload = {
            "title": "テスト",
            "isbn": "1234567890123",
            "published_date": "2000-01-01",
            "author": 99999,
        }

        # Act
        response = api_client.post(self.endpoint, payload, format="json")

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "author" in response.data


@pytest.mark.django_db
class TestBookRetrieveUpdateDelete:
    endpoint = "/api/books/"

    # --- 正常系 ---

    def test_happy_retrieve_returns_book_with_author(
        self, api_client: APIClient, book: Book
    ) -> None:
        # Act
        response = api_client.get(f"{self.endpoint}{book.pk}/")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "吾輩は猫である"
        assert isinstance(response.data["author"], dict)

    def test_happy_put_updates_book(
        self, api_client: APIClient, book: Book
    ) -> None:
        # Arrange
        payload = {
            "title": "吾輩は猫である(改訂版)",
            "isbn": book.isbn,
            "published_date": "1905-01-01",
            "author": book.author.pk,
        }

        # Act
        response = api_client.put(
            f"{self.endpoint}{book.pk}/", payload, format="json"
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        book.refresh_from_db()
        assert book.title == "吾輩は猫である(改訂版)"

    def test_happy_patch_updates_title(
        self, api_client: APIClient, book: Book
    ) -> None:
        # Arrange
        payload = {"title": "PATCHで変更"}

        # Act
        response = api_client.patch(
            f"{self.endpoint}{book.pk}/", payload, format="json"
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        book.refresh_from_db()
        assert book.title == "PATCHで変更"

    def test_happy_delete_removes_book(
        self, api_client: APIClient, book: Book
    ) -> None:
        # Act
        response = api_client.delete(f"{self.endpoint}{book.pk}/")

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Book.objects.count() == 0

    def test_happy_deleting_author_cascades_to_books(
        self, api_client: APIClient, book: Book
    ) -> None:
        # Arrange
        author_pk = book.author.pk

        # Act
        Author.objects.filter(pk=author_pk).delete()

        # Assert
        assert Book.objects.count() == 0

    # --- 異常系 ---

    @pytest.mark.parametrize(
        "method",
        ["get", "put", "patch", "delete"],
    )
    def test_error_returns_404_for_missing_book(
        self,
        api_client: APIClient,
        db: Any,
        method: str,
    ) -> None:
        """異常系: 存在しない本に対して 404 を返すこと."""
        # Arrange
        url = f"{self.endpoint}99999/"
        payload = {
            "title": "存在しない",
            "isbn": "1234567890123",
            "published_date": "2000-01-01",
            "author": 1,
        }

        # Act
        match method:
            case "get":
                response = api_client.get(url)
            case "put":
                response = api_client.put(url, payload, format="json")
            case "patch":
                response = api_client.patch(url, payload, format="json")
            case "delete":
                response = api_client.delete(url)

        # Assert
        assert response.status_code == (status.HTTP_404_NOT_FOUND)

    def test_error_put_rejects_missing_required_fields(
        self, api_client: APIClient, book: Book
    ) -> None:
        # Arrange
        payload = {"title": "タイトルだけ"}

        # Act
        response = api_client.put(
            f"{self.endpoint}{book.pk}/", payload, format="json"
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_error_patch_rejects_unsafe_title(
        self, api_client: APIClient, book: Book
    ) -> None:
        """異常系: PATCHで不正タイトルが拒否されること."""
        # Arrange
        payload = {"title": "テスト😀"}

        # Act
        response = api_client.patch(
            f"{self.endpoint}{book.pk}/",
            payload,
            format="json",
        )

        # Assert
        assert response.status_code == (status.HTTP_400_BAD_REQUEST)
        assert "title" in response.data
