from hypothesis import given
from hypothesis import strategies as st

from authors.models import Author


class TestAuthor:
    @given(name=st.text(min_size=1, max_size=255))
    def test_happy_str_returns_any_name(self, name: str) -> None:
        # Arrange
        author = Author(name=name)

        # Act
        result = str(author)

        # Assert
        assert result == name
