import pytest
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Author
from books.models import Book


@pytest.mark.django_db
class TestBookAPI:
    endpoint = "/api/books/"

    def test_list(self, api_client: APIClient, book: Book) -> None:
        response = api_client.get(self.endpoint)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert isinstance(response.data["results"][0]["author"], dict)

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

    def test_retrieve(self, api_client: APIClient, book: Book) -> None:
        response = api_client.get(f"{self.endpoint}{book.pk}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "吾輩は猫である"
        assert isinstance(response.data["author"], dict)

    def test_update(self, api_client: APIClient, book: Book) -> None:
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

    def test_delete(self, api_client: APIClient, book: Book) -> None:
        response = api_client.delete(f"{self.endpoint}{book.pk}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Book.objects.count() == 0

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
