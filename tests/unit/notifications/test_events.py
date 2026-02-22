import attrs
import pytest
from hypothesis import given
from hypothesis import strategies as st

from notifications.domain.events import AuthorCreated
from notifications.domain.events import BookCreated

_non_empty_text = st.text(min_size=1).filter(lambda s: s.strip())


class TestBookCreated:
    """BookCreated イベント値オブジェクトのテスト."""

    def test_happy_create_event(self) -> None:
        """正常にイベントが生成されること."""
        # Act
        event = BookCreated(
            title="吾輩は猫である",
            isbn="9784003101018",
            author_name="夏目漱石",
        )

        # Assert
        assert event.title == "吾輩は猫である"
        assert event.isbn == "9784003101018"
        assert event.author_name == "夏目漱石"

    def test_happy_event_is_frozen(self) -> None:
        """イベントが不変であること."""
        # Arrange
        event = BookCreated(
            title="坊っちゃん",
            isbn="9784003101025",
            author_name="夏目漱石",
        )

        # Act & Assert
        with pytest.raises(attrs.exceptions.FrozenInstanceError):
            event.title = "変更"  # type: ignore[misc]

    @given(
        title=_non_empty_text,
        isbn=_non_empty_text,
        author_name=_non_empty_text,
    )
    def test_happy_any_non_empty_strings_create_event(
        self,
        title: str,
        isbn: str,
        author_name: str,
    ) -> None:
        """任意の非空文字列でイベントが生成できること."""
        # Act
        event = BookCreated(
            title=title,
            isbn=isbn,
            author_name=author_name,
        )

        # Assert
        assert event.title == title
        assert event.isbn == isbn
        assert event.author_name == author_name

    @pytest.mark.parametrize(
        ("field", "kwargs"),
        [
            (
                "title",
                {
                    "title": "",
                    "isbn": "9784003101018",
                    "author_name": "夏目漱石",
                },
            ),
            (
                "title",
                {
                    "title": "   ",
                    "isbn": "9784003101018",
                    "author_name": "夏目漱石",
                },
            ),
            (
                "isbn",
                {
                    "title": "テスト",
                    "isbn": "",
                    "author_name": "夏目漱石",
                },
            ),
            (
                "isbn",
                {
                    "title": "テスト",
                    "isbn": "  ",
                    "author_name": "夏目漱石",
                },
            ),
            (
                "author_name",
                {
                    "title": "テスト",
                    "isbn": "9784003101018",
                    "author_name": "",
                },
            ),
            (
                "author_name",
                {
                    "title": "テスト",
                    "isbn": "9784003101018",
                    "author_name": "\t",
                },
            ),
        ],
        ids=[
            "empty_title",
            "blank_title",
            "empty_isbn",
            "blank_isbn",
            "empty_author",
            "blank_author",
        ],
    )
    def test_error_rejects_empty_or_blank_field(
        self,
        field: str,
        kwargs: dict[str, str],
    ) -> None:
        """空文字・空白のみのフィールドが拒否されること."""
        # Act & Assert
        with pytest.raises(ValueError, match=field):
            BookCreated(**kwargs)


class TestAuthorCreated:
    """AuthorCreated イベント値オブジェクトのテスト."""

    def test_happy_create_event(self) -> None:
        """正常にイベントが生成されること."""
        # Act
        event = AuthorCreated(name="太宰治")

        # Assert
        assert event.name == "太宰治"

    def test_happy_event_is_frozen(self) -> None:
        """イベントが不変であること."""
        # Arrange
        event = AuthorCreated(name="芥川龍之介")

        # Act & Assert
        with pytest.raises(attrs.exceptions.FrozenInstanceError):
            event.name = "変更"  # type: ignore[misc]

    @given(name=_non_empty_text)
    def test_happy_any_non_empty_string_creates_event(self, name: str) -> None:
        """任意の非空文字列でイベントが生成できること."""
        # Act
        event = AuthorCreated(name=name)

        # Assert
        assert event.name == name

    @pytest.mark.parametrize(
        "name",
        ["", "  ", "\t"],
        ids=["empty", "blank_spaces", "blank_tab"],
    )
    def test_error_rejects_empty_or_blank_name(self, name: str) -> None:
        """空文字・空白のみの名前が拒否されること."""
        # Act & Assert
        with pytest.raises(ValueError, match="name"):
            AuthorCreated(name=name)
