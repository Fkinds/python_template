import pytest
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Author


@pytest.mark.django_db
class TestAuthorAPI:
    endpoint = "/api/authors/"

    def test_list(self, api_client: APIClient, author: Author) -> None:
        response = api_client.get(self.endpoint)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_create(self, api_client: APIClient, db: None) -> None:
        response = api_client.post(
            self.endpoint,
            {"name": "太宰治", "bio": "走れメロスの著者"},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Author.objects.count() == 1

    def test_retrieve(self, api_client: APIClient, author: Author) -> None:
        response = api_client.get(f"{self.endpoint}{author.pk}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "夏目漱石"

    def test_update(self, api_client: APIClient, author: Author) -> None:
        response = api_client.put(
            f"{self.endpoint}{author.pk}/",
            {"name": "夏目漱石", "bio": "更新されたプロフィール"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        author.refresh_from_db()
        assert author.bio == "更新されたプロフィール"

    def test_delete(self, api_client: APIClient, author: Author) -> None:
        response = api_client.delete(f"{self.endpoint}{author.pk}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Author.objects.count() == 0
