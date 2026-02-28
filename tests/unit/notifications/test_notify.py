import logging
from http import HTTPStatus
from unittest.mock import create_autospec

from hypothesis import given
from hypothesis import strategies as st

from common.infrastructure.factories.logger import LoggerFactoryImpl
from common.usecases.protocols import LoggerFactory
from notifications.domain.events import AuthorCreated
from notifications.domain.events import BookCreated
from notifications.domain.notification_channel import NotificationChannel
from notifications.domain.results import NotificationProblem
from notifications.domain.results import NotificationSuccess
from notifications.infrastructure.adapters.fake import (
    FakeNotificationLogWriter,
)
from notifications.infrastructure.adapters.fake import FakeNotifier
from notifications.usecases.notify import NotifyAuthorCreatedUseCaseImpl
from notifications.usecases.notify import NotifyBookCreatedUseCaseImpl

_non_empty_text = st.text(min_size=1).filter(lambda s: s.strip())
_real_factory = LoggerFactoryImpl()


class _StubLoggerFactory:
    """テスト用: 固定の mock Logger を返すファクトリ."""

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def build(self, name: str) -> logging.Logger:
        return self._logger


class _FailingNotifier:
    """send 時に例外を投げるテスト用 Notifier."""

    def send(self, message: str) -> None:
        msg = "送信失敗"
        raise RuntimeError(msg)


class _FailingLogWriter:
    """save 時に例外を投げるテスト用 Writer."""

    def save(
        self,
        *,
        event_type: str,
        message: str,
        status: str,
        detail: str,
        recipient: str,
        channel: str,
        retry_count: int,
    ) -> None:
        msg = "保存失敗"
        raise RuntimeError(msg)


class TestNotifyBookCreatedUseCaseImpl:
    """本の作成通知ユースケースのテスト."""

    def test_happy_sends_message_with_title_and_author(
        self,
    ) -> None:
        """タイトルと著者名を含むメッセージが送信されること."""
        # Arrange
        fake = FakeNotifier()
        writer = FakeNotificationLogWriter()
        use_case = NotifyBookCreatedUseCaseImpl(
            notifier=fake,
            logger_factory=_real_factory,
            log_writer=writer,
            channel=NotificationChannel.FAKE,
        )
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
        writer = FakeNotificationLogWriter()
        use_case = NotifyBookCreatedUseCaseImpl(
            notifier=fake,
            logger_factory=_real_factory,
            log_writer=writer,
            channel=NotificationChannel.FAKE,
        )
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

    def test_happy_saves_success_log_after_send(
        self,
    ) -> None:
        """送信成功時に履歴が保存されること."""
        # Arrange
        fake = FakeNotifier()
        writer = FakeNotificationLogWriter()
        use_case = NotifyBookCreatedUseCaseImpl(
            notifier=fake,
            logger_factory=_real_factory,
            log_writer=writer,
            channel=NotificationChannel.FAKE,
        )
        event = BookCreated(
            title="テスト本",
            isbn="9784003101018",
            author_name="テスト著者",
        )

        # Act
        use_case.execute(event=event)

        # Assert
        assert len(writer.logs) == 1
        log = writer.logs[0]
        assert log["event_type"] == "book_created"
        assert log["status"] == "success"
        assert log["channel"] == "fake"

    def test_happy_saves_failure_log_on_notifier_error(
        self,
    ) -> None:
        """Notifier 失敗時に failure 履歴が保存されること."""
        # Arrange
        writer = FakeNotificationLogWriter()
        use_case = NotifyBookCreatedUseCaseImpl(
            notifier=_FailingNotifier(),
            logger_factory=_real_factory,
            log_writer=writer,
            channel=NotificationChannel.FAKE,
        )
        event = BookCreated(
            title="テスト",
            isbn="9784003101018",
            author_name="テスト著者",
        )

        # Act
        use_case.execute(event=event)

        # Assert
        assert len(writer.logs) == 1
        log = writer.logs[0]
        assert log["status"] == "failure"

    def test_happy_succeeds_even_when_log_writer_fails(
        self,
    ) -> None:
        """履歴保存に失敗しても通知結果は成功で返ること."""
        # Arrange
        fake = FakeNotifier()
        use_case = NotifyBookCreatedUseCaseImpl(
            notifier=fake,
            logger_factory=_real_factory,
            log_writer=_FailingLogWriter(),
            channel=NotificationChannel.FAKE,
        )
        event = BookCreated(
            title="テスト",
            isbn="9784003101018",
            author_name="テスト著者",
        )

        # Act
        result = use_case.execute(event=event)

        # Assert
        assert isinstance(result, NotificationSuccess)

    def test_error_returns_problem_on_notifier_failure(
        self,
    ) -> None:
        """Notifier 失敗時に NotificationProblem が返ること."""
        # Arrange
        writer = FakeNotificationLogWriter()
        use_case = NotifyBookCreatedUseCaseImpl(
            notifier=_FailingNotifier(),
            logger_factory=_real_factory,
            log_writer=writer,
            channel=NotificationChannel.FAKE,
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

    def test_error_logs_warning_on_notifier_failure(
        self,
    ) -> None:
        """Notifier 失敗時に warning ログが出力されること."""
        # Arrange
        mock_logger = create_autospec(
            logging.Logger,
            instance=True,
        )
        factory: LoggerFactory = _StubLoggerFactory(mock_logger)
        writer = FakeNotificationLogWriter()
        use_case = NotifyBookCreatedUseCaseImpl(
            notifier=_FailingNotifier(),
            logger_factory=factory,
            log_writer=writer,
            channel=NotificationChannel.FAKE,
        )
        event = BookCreated(
            title="テスト本",
            isbn="9784003101018",
            author_name="テスト著者",
        )

        # Act
        use_case.execute(event=event)

        # Assert
        mock_logger.warning.assert_any_call(
            "本作成通知の送信に失敗: title=%s",
            "テスト本",
            exc_info=True,
        )


class TestNotifyAuthorCreatedUseCaseImpl:
    """著者の作成通知ユースケースのテスト."""

    def test_happy_sends_message_with_name(
        self,
    ) -> None:
        """著者名を含むメッセージが送信されること."""
        # Arrange
        fake = FakeNotifier()
        writer = FakeNotificationLogWriter()
        use_case = NotifyAuthorCreatedUseCaseImpl(
            notifier=fake,
            logger_factory=_real_factory,
            log_writer=writer,
            channel=NotificationChannel.FAKE,
        )
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
        writer = FakeNotificationLogWriter()
        use_case = NotifyAuthorCreatedUseCaseImpl(
            notifier=fake,
            logger_factory=_real_factory,
            log_writer=writer,
            channel=NotificationChannel.FAKE,
        )
        event = AuthorCreated(name=name)

        # Act
        result = use_case.execute(event=event)

        # Assert
        assert isinstance(result, NotificationSuccess)
        (msg,) = fake.messages
        assert name in msg

    def test_happy_saves_success_log_after_send(
        self,
    ) -> None:
        """送信成功時に履歴が保存されること."""
        # Arrange
        fake = FakeNotifier()
        writer = FakeNotificationLogWriter()
        use_case = NotifyAuthorCreatedUseCaseImpl(
            notifier=fake,
            logger_factory=_real_factory,
            log_writer=writer,
            channel=NotificationChannel.FAKE,
        )
        event = AuthorCreated(name="テスト著者")

        # Act
        use_case.execute(event=event)

        # Assert
        assert len(writer.logs) == 1
        log = writer.logs[0]
        assert log["event_type"] == "author_created"
        assert log["status"] == "success"

    def test_error_returns_problem_on_notifier_failure(
        self,
    ) -> None:
        """Notifier 失敗時に NotificationProblem が返ること."""
        # Arrange
        writer = FakeNotificationLogWriter()
        use_case = NotifyAuthorCreatedUseCaseImpl(
            notifier=_FailingNotifier(),
            logger_factory=_real_factory,
            log_writer=writer,
            channel=NotificationChannel.FAKE,
        )
        event = AuthorCreated(name="テスト著者")

        # Act
        result = use_case.execute(event=event)

        # Assert
        assert isinstance(result, NotificationProblem)
        assert result.status == HTTPStatus.BAD_GATEWAY
        assert "テスト著者" in result.detail

    def test_error_logs_warning_on_notifier_failure(
        self,
    ) -> None:
        """Notifier 失敗時に warning ログが出力されること."""
        # Arrange
        mock_logger = create_autospec(
            logging.Logger,
            instance=True,
        )
        factory: LoggerFactory = _StubLoggerFactory(mock_logger)
        writer = FakeNotificationLogWriter()
        use_case = NotifyAuthorCreatedUseCaseImpl(
            notifier=_FailingNotifier(),
            logger_factory=factory,
            log_writer=writer,
            channel=NotificationChannel.FAKE,
        )
        event = AuthorCreated(name="テスト著者")

        # Act
        use_case.execute(event=event)

        # Assert
        mock_logger.warning.assert_any_call(
            "著者作成通知の送信に失敗: name=%s",
            "テスト著者",
            exc_info=True,
        )
