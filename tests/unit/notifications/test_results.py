from http import HTTPStatus

import attrs
import pytest

from notifications.domain.results import NotificationProblem
from notifications.domain.results import NotificationSuccess


class TestNotificationSuccess:
    """NotificationSuccess 値オブジェクトのテスト."""

    def test_happy_create_success_with_defaults(
        self,
    ) -> None:
        """デフォルト status=200 で成功結果が生成されること."""
        # Act
        result = NotificationSuccess(message="テスト通知")

        # Assert
        assert result.status == HTTPStatus.OK
        assert result.message == "テスト通知"

    def test_happy_create_success_with_custom_status(
        self,
    ) -> None:
        """status を明示指定できること."""
        # Act
        result = NotificationSuccess(
            status=HTTPStatus.NO_CONTENT,
            message="テスト通知",
        )

        # Assert
        assert result.status == HTTPStatus.NO_CONTENT

    def test_happy_is_frozen(self) -> None:
        """成功結果が不変であること."""
        # Arrange
        result = NotificationSuccess(message="テスト")

        # Act & Assert
        with pytest.raises(
            attrs.exceptions.FrozenInstanceError,
        ):
            result.message = "変更"  # type: ignore[misc]


class TestNotificationProblem:
    """NotificationProblem 値オブジェクトのテスト."""

    def test_happy_create_problem_with_defaults(
        self,
    ) -> None:
        """デフォルト値でエラー結果が生成されること."""
        # Act
        result = NotificationProblem(
            title="Notification Failed",
            status=HTTPStatus.BAD_GATEWAY,
            detail="送信に失敗しました",
        )

        # Assert
        assert result.type_uri == "about:blank"
        assert result.title == "Notification Failed"
        assert result.status == HTTPStatus.BAD_GATEWAY
        assert result.detail == "送信に失敗しました"
        assert result.instance == ""

    def test_happy_create_problem_with_all_fields(
        self,
    ) -> None:
        """全フィールド指定でエラー結果が生成されること."""
        # Act
        result = NotificationProblem(
            type_uri="urn:notification:delivery-failed",
            title="Delivery Failed",
            status=HTTPStatus.BAD_GATEWAY,
            detail="Discord webhook timed out",
            instance="/api/books/42",
        )

        # Assert
        assert result.type_uri == ("urn:notification:delivery-failed")
        assert result.instance == "/api/books/42"

    def test_happy_is_frozen(self) -> None:
        """エラー結果が不変であること."""
        # Arrange
        result = NotificationProblem(
            title="Error",
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="テスト",
        )

        # Act & Assert
        with pytest.raises(
            attrs.exceptions.FrozenInstanceError,
        ):
            result.title = "変更"  # type: ignore[misc]
