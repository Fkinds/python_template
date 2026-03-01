import pytest
from hypothesis import given
from hypothesis import strategies as st

from books.entities import Book
from books.entities.safe_text import SafeText


class TestBook:
    @given(title=st.text(min_size=1, max_size=255))
    def test_happy_str_returns_any_title(self, title: str) -> None:
        # Arrange
        book = Book(title=title)

        # Act
        result = str(book)

        # Assert
        assert result == title

    @pytest.mark.parametrize(
        "title",
        ["吾輩は猫である", "Clean Code"],
        ids=["japanese", "english"],
    )
    def test_happy_title_vo_returns_safe_text(self, title: str) -> None:
        """正常系: title_vo が SafeText を返すこと."""
        # Arrange
        book = Book(title=title)

        # Act
        vo = book.title_vo

        # Assert
        assert isinstance(vo, SafeText)
        assert vo.value == title

    def test_error_title_vo_raises_for_unsafe_chars(
        self,
    ) -> None:
        """異常系: 不正文字で title_vo が ValueError になること."""
        # Arrange
        book = Book(title="テスト😀")

        # Act & Assert
        with pytest.raises(ValueError, match="使用できない文字"):
            _ = book.title_vo
