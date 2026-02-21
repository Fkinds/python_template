from typing import Any

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Author


@pytest.mark.django_db
class TestAuthorListCreate:
    endpoint = "/api/authors/"

    # --- 正常系 ---

    def test_list_empty(self, api_client: APIClient, db: Any) -> None:
        response = api_client.get(self.endpoint)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
        assert response.data["results"] == []

    def test_list_with_data(
        self, api_client: APIClient, author: Author
    ) -> None:
        response = api_client.get(self.endpoint)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_create(self, api_client: APIClient, db: Any) -> None:
        response = api_client.post(
            self.endpoint,
            {"name": "太宰治", "bio": "走れメロスの著者"},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Author.objects.count() == 1
        assert response.data["name"] == "太宰治"
        assert response.data["bio"] == "走れメロスの著者"
        assert "id" in response.data
        assert "created_at" in response.data

    def test_create_without_bio(self, api_client: APIClient, db: Any) -> None:
        response = api_client.post(
            self.endpoint,
            {"name": "芥川龍之介"},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["bio"] == ""

    # --- 異常系 ---

    def test_create_missing_name(self, api_client: APIClient, db: Any) -> None:
        response = api_client.post(
            self.endpoint,
            {"bio": "名前なし"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data

    def test_create_empty_name(self, api_client: APIClient, db: Any) -> None:
        response = api_client.post(
            self.endpoint,
            {"name": ""},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data

    def test_create_name_too_long(
        self, api_client: APIClient, db: Any
    ) -> None:
        response = api_client.post(
            self.endpoint,
            {"name": "a" * 256},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data

    def test_create_empty_body(self, api_client: APIClient, db: Any) -> None:
        response = api_client.post(self.endpoint, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestAuthorRetrieveUpdateDelete:
    endpoint = "/api/authors/"

    # --- 正常系 ---

    def test_retrieve(self, api_client: APIClient, author: Author) -> None:
        response = api_client.get(f"{self.endpoint}{author.pk}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "夏目漱石"
        assert response.data["id"] == author.pk

    def test_update_put(self, api_client: APIClient, author: Author) -> None:
        response = api_client.put(
            f"{self.endpoint}{author.pk}/",
            {"name": "夏目漱石", "bio": "更新済み"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        author.refresh_from_db()
        assert author.bio == "更新済み"

    def test_partial_update_patch(
        self, api_client: APIClient, author: Author
    ) -> None:
        response = api_client.patch(
            f"{self.endpoint}{author.pk}/",
            {"bio": "PATCHで更新"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        author.refresh_from_db()
        assert author.bio == "PATCHで更新"
        assert author.name == "夏目漱石"

    def test_delete(self, api_client: APIClient, author: Author) -> None:
        response = api_client.delete(f"{self.endpoint}{author.pk}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Author.objects.count() == 0

    # --- 異常系 ---

    def test_retrieve_not_found(self, api_client: APIClient, db: Any) -> None:
        response = api_client.get(f"{self.endpoint}99999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_not_found(self, api_client: APIClient, db: Any) -> None:
        response = api_client.put(
            f"{self.endpoint}99999/",
            {"name": "存在しない"},
            format="json",
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_not_found(self, api_client: APIClient, db: Any) -> None:
        response = api_client.delete(f"{self.endpoint}99999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_put_missing_required_field(
        self, api_client: APIClient, author: Author
    ) -> None:
        response = api_client.put(
            f"{self.endpoint}{author.pk}/",
            {"bio": "nameなし"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data
