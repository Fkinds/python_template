from hypothesis import given
from hypothesis import strategies as st

from authors.models import Author


class TestAuthor:
    def test_happy_str_returns_name(self) -> None:
        # Arrange
        author = Author(name="夏目漱石")

        # Act
        result = str(author)

        # Assert
        assert result == "夏目漱石"

    @given(name=st.text(min_size=1, max_size=255))
    def test_happy_str_returns_any_name(self, name: str) -> None:
        # Arrange
        author = Author(name=name)

        # Act
        result = str(author)

        # Assert
        assert result == name

    def test_happy_str_returns_empty_for_no_name(self) -> None:
        # Arrange
        author = Author(name="")

        # Act
        result = str(author)

        # Assert
        assert result == ""

    def test_happy_orders_by_name(self) -> None:
        # Assert
        assert "name" in Author._meta.ordering

    def test_happy_name_max_length_is_255(self) -> None:
        # Arrange & Act
        field = Author._meta.get_field("name")

        # Assert
        assert field.max_length == 255

    def test_happy_bio_allows_blank(self) -> None:
        # Arrange & Act
        field = Author._meta.get_field("bio")

        # Assert
        assert field.blank is True

    def test_happy_bio_defaults_to_empty(self) -> None:
        # Arrange & Act
        field = Author._meta.get_field("bio")

        # Assert
        assert field.default == ""

    def test_happy_created_at_auto_sets(self) -> None:
        # Arrange & Act
        field = Author._meta.get_field("created_at")

        # Assert
        assert field.auto_now_add is True
