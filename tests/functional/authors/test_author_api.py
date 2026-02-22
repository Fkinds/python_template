from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st
from rest_framework import status
from rest_framework.test import APIClient

from authors.models import Author
from notifications.infrastructure.adapters.fake import FakeNotifier
from notifications.infrastructure.containers.notificaton import (
    override_notifier,
)


@pytest.mark.django_db
class TestAuthorListCreate:
    endpoint = "/api/authors/"

    # --- 正常系 ---

    def test_happy_list_returns_zero_count_when_empty(
        self, api_client: APIClient, db: Any
    ) -> None:
        # Act
        response = api_client.get(self.endpoint)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

    def test_happy_list_returns_authors(
        self, api_client: APIClient, author: Author
    ) -> None:
        # Act
        response = api_client.get(self.endpoint)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_happy_create_author_with_bio(
        self, api_client: APIClient, db: Any
    ) -> None:
        # Arrange
        payload = {"name": "太宰治", "bio": "走れメロスの著者"}

        # Act
        response = api_client.post(self.endpoint, payload, format="json")

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert Author.objects.count() == 1
        assert response.data["name"] == "太宰治"
        assert response.data["bio"] == "走れメロスの著者"
        assert "id" in response.data
        assert "created_at" in response.data

    def test_happy_create_sends_notification(
        self,
        api_client: APIClient,
        db: Any,
        fake_notifier: FakeNotifier,
    ) -> None:
        """著者の作成時に通知が送信されること."""
        # Arrange
        payload = {"name": "太宰治", "bio": "走れメロスの著者"}

        # Act
        api_client.post(self.endpoint, payload, format="json")

        # Assert
        assert len(fake_notifier.messages) == 1
        (msg,) = fake_notifier.messages
        assert "太宰治" in msg

    def test_happy_create_succeeds_despite_notification_failure(
        self,
        api_client: APIClient,
        db: Any,
    ) -> None:
        """通知送信失敗時でも著者の作成は成功すること."""

        # Arrange
        class _FailingNotifier:
            def send(self, message: str) -> None:
                msg = "Discord 障害"
                raise RuntimeError(msg)

        override_notifier(notifier=_FailingNotifier())
        payload = {"name": "太宰治"}

        # Act
        response = api_client.post(
            self.endpoint,
            payload,
            format="json",
        )

        # Assert
        assert response.status_code == (status.HTTP_201_CREATED)
        assert Author.objects.count() == 1

        # Cleanup
        override_notifier(notifier=None)

    def test_happy_create_author_without_bio(
        self, api_client: APIClient, db: Any
    ) -> None:
        # Arrange
        payload = {"name": "芥川龍之介"}

        # Act
        response = api_client.post(self.endpoint, payload, format="json")

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["bio"] == ""

    @given(
        name=st.text(
            min_size=1,
            max_size=255,
            alphabet=st.characters(
                blacklist_categories=("Cs",),
                blacklist_characters="\x00",
            ),
        ).filter(lambda s: s.strip())
    )
    def test_happy_create_accepts_any_valid_name(self, name: str) -> None:
        # Arrange
        Author.objects.all().delete()
        client = APIClient()
        payload = {"name": name}

        # Act
        response = client.post(self.endpoint, payload, format="json")

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == name.strip()

    # --- 異常系 ---

    def test_error_create_rejects_missing_name(
        self, api_client: APIClient, db: Any
    ) -> None:
        # Arrange
        payload = {"bio": "名前なし"}

        # Act
        response = api_client.post(self.endpoint, payload, format="json")

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data

    def test_error_create_rejects_empty_name(
        self, api_client: APIClient, db: Any
    ) -> None:
        # Arrange
        payload = {"name": ""}

        # Act
        response = api_client.post(self.endpoint, payload, format="json")

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data

    def test_error_create_rejects_name_too_long(
        self, api_client: APIClient, db: Any
    ) -> None:
        # Arrange
        payload = {"name": "a" * 256}

        # Act
        response = api_client.post(self.endpoint, payload, format="json")

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data

    def test_error_create_rejects_empty_body(
        self, api_client: APIClient, db: Any
    ) -> None:
        # Arrange
        payload: dict[str, str] = {}

        # Act
        response = api_client.post(self.endpoint, payload, format="json")

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestAuthorRetrieveUpdateDelete:
    endpoint = "/api/authors/"

    # --- 正常系 ---

    def test_happy_retrieve_returns_author(
        self, api_client: APIClient, author: Author
    ) -> None:
        # Act
        response = api_client.get(f"{self.endpoint}{author.pk}/")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "夏目漱石"
        assert response.data["id"] == author.pk

    def test_happy_put_updates_author(
        self, api_client: APIClient, author: Author
    ) -> None:
        # Arrange
        payload = {"name": "夏目漱石", "bio": "更新済み"}

        # Act
        response = api_client.put(
            f"{self.endpoint}{author.pk}/", payload, format="json"
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        author.refresh_from_db()
        assert author.bio == "更新済み"

    def test_happy_patch_updates_bio_only(
        self, api_client: APIClient, author: Author
    ) -> None:
        # Arrange
        payload = {"bio": "PATCHで更新"}

        # Act
        response = api_client.patch(
            f"{self.endpoint}{author.pk}/", payload, format="json"
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        author.refresh_from_db()
        assert author.bio == "PATCHで更新"
        assert author.name == "夏目漱石"

    def test_happy_delete_removes_author(
        self, api_client: APIClient, author: Author
    ) -> None:
        # Act
        response = api_client.delete(f"{self.endpoint}{author.pk}/")

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Author.objects.count() == 0

    # --- 異常系 ---

    @pytest.mark.parametrize(
        "method",
        ["get", "put", "patch", "delete"],
    )
    def test_error_returns_404_for_missing_author(
        self,
        api_client: APIClient,
        db: Any,
        method: str,
    ) -> None:
        """異常系: 存在しない著者に対して 404 を返すこと."""
        # Arrange
        url = f"{self.endpoint}99999/"
        payload = {"name": "存在しない"}

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

    def test_error_put_rejects_missing_name(
        self, api_client: APIClient, author: Author
    ) -> None:
        # Arrange
        payload = {"bio": "nameなし"}

        # Act
        response = api_client.put(
            f"{self.endpoint}{author.pk}/", payload, format="json"
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data
