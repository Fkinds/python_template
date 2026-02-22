from http import HTTPStatus

from hypothesis import given
from hypothesis import strategies as st

from notifications.domain.events import AuthorCreated
from notifications.domain.events import BookCreated
from notifications.domain.results import NotificationProblem
from notifications.domain.results import NotificationSuccess
from notifications.infrastructure.adapters.fake import FakeNotifier
from notifications.usecases.notify import NotifyAuthorCreatedUseCaseImpl
from notifications.usecases.notify import NotifyBookCreatedUseCaseImpl

_non_empty_text = st.text(min_size=1).filter(lambda s: s.strip())


class _FailingNotifier:
    """send 時に例外を投げるテスト用 Notifier."""

    def send(self, message: str) -> None:
        msg = "送信失敗"
        raise RuntimeError(msg)


class TestNotifyBookCreatedUseCaseImpl:
    """本の作成通知ユースケースのテスト."""

    def test_happy_sends_message_with_title_and_author(
        self,
    ) -> None:
        """タイトルと著者名を含むメッセージが送信されること."""
        # Arrange
        fake = FakeNotifier()
        use_case = NotifyBookCreatedUseCaseImpl(notifier=fake)
        event = BookCreated(
            title="吾輩は猫である",
            isbn="9784003101018",
            author_name="夏目漱石",
        )

        # Act
        result = use_case.execute(event=event)

        # Assert
        assert isinstance(result, NotificationSuccess)
        assert len(fake.messages) == 1
        (msg,) = fake.messages
        assert "吾輩は猫である" in msg
        assert "夏目漱石" in msg

    @given(
        title=_non_empty_text,
        isbn=_non_empty_text,
        author_name=_non_empty_text,
    )
    def test_happy_message_contains_event_fields(
        self,
        title: str,
        isbn: str,
        author_name: str,
    ) -> None:
        """メッセージにイベントのフィールドが含まれること."""
        # Arrange
        fake = FakeNotifier()
        use_case = NotifyBookCreatedUseCaseImpl(notifier=fake)
        event = BookCreated(
            title=title,
            isbn=isbn,
            author_name=author_name,
        )

        # Act
        result = use_case.execute(event=event)

        # Assert
        assert isinstance(result, NotificationSuccess)
        (msg,) = fake.messages
        assert title in msg
        assert author_name in msg

    def test_error_returns_problem_on_notifier_failure(
        self,
    ) -> None:
        """Notifier 失敗時に NotificationProblem が返ること."""
        # Arrange
        use_case = NotifyBookCreatedUseCaseImpl(
            notifier=_FailingNotifier(),
        )
        event = BookCreated(
            title="テスト",
            isbn="9784003101018",
            author_name="テスト著者",
        )

        # Act
        result = use_case.execute(event=event)

        # Assert
        assert isinstance(result, NotificationProblem)
        assert result.status == HTTPStatus.BAD_GATEWAY
        assert "テスト" in result.detail


class TestNotifyAuthorCreatedUseCaseImpl:
    """著者の作成通知ユースケースのテスト."""

    def test_happy_sends_message_with_name(self) -> None:
        """著者名を含むメッセージが送信されること."""
        # Arrange
        fake = FakeNotifier()
        use_case = NotifyAuthorCreatedUseCaseImpl(notifier=fake)
        event = AuthorCreated(name="太宰治")

        # Act
        result = use_case.execute(event=event)

        # Assert
        assert isinstance(result, NotificationSuccess)
        assert len(fake.messages) == 1
        (msg,) = fake.messages
        assert "太宰治" in msg

    @given(name=_non_empty_text)
    def test_happy_message_contains_name(self, name: str) -> None:
        """メッセージに著者名が含まれること."""
        # Arrange
        fake = FakeNotifier()
        use_case = NotifyAuthorCreatedUseCaseImpl(notifier=fake)
        event = AuthorCreated(name=name)

        # Act
        result = use_case.execute(event=event)

        # Assert
        assert isinstance(result, NotificationSuccess)
        (msg,) = fake.messages
        assert name in msg

    def test_error_returns_problem_on_notifier_failure(
        self,
    ) -> None:
        """Notifier 失敗時に NotificationProblem が返ること."""
        # Arrange
        use_case = NotifyAuthorCreatedUseCaseImpl(
            notifier=_FailingNotifier(),
        )
        event = AuthorCreated(name="テスト著者")

        # Act
        result = use_case.execute(event=event)

        # Assert
        assert isinstance(result, NotificationProblem)
        assert result.status == HTTPStatus.BAD_GATEWAY
        assert "テスト著者" in result.detail
