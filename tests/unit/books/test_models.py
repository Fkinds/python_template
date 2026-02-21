from hypothesis import given
from hypothesis import strategies as st

from books.models import Book


class TestBook:
    def test_happy_str_returns_title(self) -> None:
        # Arrange
        book = Book(title="吾輩は猫である")

        # Act
        result = str(book)

        # Assert
        assert result == "吾輩は猫である"

    @given(title=st.text(min_size=1, max_size=255))
    def test_happy_str_returns_any_title(self, title: str) -> None:
        # Arrange
        book = Book(title=title)

        # Act
        result = str(book)

        # Assert
        assert result == title

    def test_happy_str_returns_empty_for_no_title(self) -> None:
        # Arrange
        book = Book(title="")

        # Act
        result = str(book)

        # Assert
        assert result == ""

    def test_happy_orders_by_published_date_desc(self) -> None:
        # Assert
        assert "-published_date" in Book._meta.ordering

    def test_happy_has_expected_fields(self) -> None:
        # Arrange
        expected = {
            "title",
            "isbn",
            "published_date",
            "author",
            "created_at",
        }

        # Act
        field_names = {f.name for f in Book._meta.get_fields()}

        # Assert
        assert expected <= field_names

    def test_happy_title_max_length_is_255(self) -> None:
        # Arrange & Act
        field = Book._meta.get_field("title")

        # Assert
        assert field.max_length == 255

    def test_happy_isbn_max_length_is_13(self) -> None:
        # Arrange & Act
        field = Book._meta.get_field("isbn")

        # Assert
        assert field.max_length == 13

    def test_happy_isbn_is_unique(self) -> None:
        # Arrange & Act
        field = Book._meta.get_field("isbn")

        # Assert
        assert field.unique is True

    def test_happy_author_cascades_on_delete(self) -> None:
        from django.db import models

        # Arrange & Act
        field = Book._meta.get_field("author")

        # Assert
        assert field.remote_field.on_delete is models.CASCADE

    def test_happy_author_related_name_is_books(self) -> None:
        # Arrange & Act
        field = Book._meta.get_field("author")

        # Assert
        assert field.remote_field.related_name == "books"

    def test_happy_created_at_auto_sets(self) -> None:
        # Arrange & Act
        field = Book._meta.get_field("created_at")

        # Assert
        assert field.auto_now_add is True
