from typing import Any

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Author
from books.models import Book


@pytest.mark.django_db
class TestBookListCreate:
    endpoint = "/api/books/"

    # --- 正常系 ---

    def test_list_empty(self, api_client: APIClient, db: Any) -> None:
        response = api_client.get(self.endpoint)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

    def test_list_returns_nested_author(
        self, api_client: APIClient, book: Book
    ) -> None:
        response = api_client.get(self.endpoint)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        result = response.data["results"][0]
        assert isinstance(result["author"], dict)
        assert "name" in result["author"]

    def test_create(self, api_client: APIClient, author: Author) -> None:
        response = api_client.post(
            self.endpoint,
            {
                "title": "坊っちゃん",
                "isbn": "9784003101025",
                "published_date": "1906-04-01",
                "author": author.pk,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Book.objects.count() == 1
        assert response.data["title"] == "坊っちゃん"

    # --- 異常系 ---

    def test_create_empty_body(self, api_client: APIClient, db: Any) -> None:
        response = api_client.post(self.endpoint, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        missing = {"title", "isbn", "published_date", "author"}
        assert missing <= set(response.data.keys())

    def test_create_missing_title(
        self, api_client: APIClient, author: Author
    ) -> None:
        response = api_client.post(
            self.endpoint,
            {
                "isbn": "9784003101025",
                "published_date": "1906-04-01",
                "author": author.pk,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "title" in response.data

    def test_create_missing_isbn(
        self, api_client: APIClient, author: Author
    ) -> None:
        response = api_client.post(
            self.endpoint,
            {
                "title": "テスト",
                "published_date": "1906-04-01",
                "author": author.pk,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "isbn" in response.data

    def test_create_duplicate_isbn(
        self, api_client: APIClient, book: Book
    ) -> None:
        response = api_client.post(
            self.endpoint,
            {
                "title": "重複テスト",
                "isbn": book.isbn,
                "published_date": "2000-01-01",
                "author": book.author.pk,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "isbn" in response.data

    def test_create_isbn_too_long(
        self, api_client: APIClient, author: Author
    ) -> None:
        response = api_client.post(
            self.endpoint,
            {
                "title": "テスト",
                "isbn": "12345678901234",
                "published_date": "2000-01-01",
                "author": author.pk,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "isbn" in response.data

    def test_create_invalid_date(
        self, api_client: APIClient, author: Author
    ) -> None:
        response = api_client.post(
            self.endpoint,
            {
                "title": "テスト",
                "isbn": "1234567890123",
                "published_date": "not-a-date",
                "author": author.pk,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "published_date" in response.data

    def test_create_nonexistent_author(
        self, api_client: APIClient, db: Any
    ) -> None:
        response = api_client.post(
            self.endpoint,
            {
                "title": "テスト",
                "isbn": "1234567890123",
                "published_date": "2000-01-01",
                "author": 99999,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "author" in response.data


@pytest.mark.django_db
class TestBookRetrieveUpdateDelete:
    endpoint = "/api/books/"

    # --- 正常系 ---

    def test_retrieve(self, api_client: APIClient, book: Book) -> None:
        response = api_client.get(f"{self.endpoint}{book.pk}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "吾輩は猫である"
        assert isinstance(response.data["author"], dict)

    def test_update_put(self, api_client: APIClient, book: Book) -> None:
        response = api_client.put(
            f"{self.endpoint}{book.pk}/",
            {
                "title": "吾輩は猫である(改訂版)",
                "isbn": book.isbn,
                "published_date": "1905-01-01",
                "author": book.author.pk,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        book.refresh_from_db()
        assert book.title == "吾輩は猫である(改訂版)"

    def test_partial_update_patch(
        self, api_client: APIClient, book: Book
    ) -> None:
        response = api_client.patch(
            f"{self.endpoint}{book.pk}/",
            {"title": "PATCHで変更"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        book.refresh_from_db()
        assert book.title == "PATCHで変更"

    def test_delete(self, api_client: APIClient, book: Book) -> None:
        response = api_client.delete(f"{self.endpoint}{book.pk}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Book.objects.count() == 0

    # --- 異常系 ---

    def test_retrieve_not_found(self, api_client: APIClient, db: Any) -> None:
        response = api_client.get(f"{self.endpoint}99999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_not_found(self, api_client: APIClient, db: Any) -> None:
        response = api_client.put(
            f"{self.endpoint}99999/",
            {
                "title": "存在しない",
                "isbn": "1234567890123",
                "published_date": "2000-01-01",
                "author": 1,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_not_found(self, api_client: APIClient, db: Any) -> None:
        response = api_client.delete(f"{self.endpoint}99999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_put_missing_required_fields(
        self, api_client: APIClient, book: Book
    ) -> None:
        response = api_client.put(
            f"{self.endpoint}{book.pk}/",
            {"title": "タイトルだけ"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cascade_delete_author(
        self, api_client: APIClient, book: Book
    ) -> None:
        author_pk = book.author.pk
        Author.objects.filter(pk=author_pk).delete()
        assert Book.objects.count() == 0
