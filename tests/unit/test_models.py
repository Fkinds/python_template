from hypothesis import given
from hypothesis import strategies as st

from books.models import Author
from books.models import Book


class TestAuthor:
    def test_str(self) -> None:
        # Arrange
        author = Author(name="夏目漱石")

        # Act
        result = str(author)

        # Assert
        assert result == "夏目漱石"

    @given(name=st.text(min_size=1, max_size=255))
    def test_str_returns_name(self, name: str) -> None:
        # Arrange
        author = Author(name=name)

        # Act
        result = str(author)

        # Assert
        assert result == name

    def test_str_empty_name(self) -> None:
        # Arrange
        author = Author(name="")

        # Act
        result = str(author)

        # Assert
        assert result == ""

    def test_meta_ordering(self) -> None:
        # Arrange & Act
        ordering = Author._meta.ordering

        # Assert
        assert ordering == ["name"]

    def test_name_max_length(self) -> None:
        # Arrange & Act
        field = Author._meta.get_field("name")

        # Assert
        assert field.max_length == 255

    def test_bio_blank_allowed(self) -> None:
        # Arrange & Act
        field = Author._meta.get_field("bio")

        # Assert
        assert field.blank is True

    def test_bio_default_empty(self) -> None:
        # Arrange & Act
        field = Author._meta.get_field("bio")

        # Assert
        assert field.default == ""

    def test_created_at_auto_now_add(self) -> None:
        # Arrange & Act
        field = Author._meta.get_field("created_at")

        # Assert
        assert field.auto_now_add is True


class TestBook:
    def test_str(self) -> None:
        # Arrange
        book = Book(title="吾輩は猫である")

        # Act
        result = str(book)

        # Assert
        assert result == "吾輩は猫である"

    @given(title=st.text(min_size=1, max_size=255))
    def test_str_returns_title(self, title: str) -> None:
        # Arrange
        book = Book(title=title)

        # Act
        result = str(book)

        # Assert
        assert result == title

    def test_str_empty_title(self) -> None:
        # Arrange
        book = Book(title="")

        # Act
        result = str(book)

        # Assert
        assert result == ""

    def test_meta_ordering(self) -> None:
        # Arrange & Act
        ordering = Book._meta.ordering

        # Assert
        assert ordering == ["-published_date"]

    def test_expected_fields_exist(self) -> None:
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

    def test_title_max_length(self) -> None:
        # Arrange & Act
        field = Book._meta.get_field("title")

        # Assert
        assert field.max_length == 255

    def test_isbn_max_length(self) -> None:
        # Arrange & Act
        field = Book._meta.get_field("isbn")

        # Assert
        assert field.max_length == 13

    def test_isbn_unique(self) -> None:
        # Arrange & Act
        field = Book._meta.get_field("isbn")

        # Assert
        assert field.unique is True

    def test_author_cascade_delete(self) -> None:
        from django.db import models

        # Arrange & Act
        field = Book._meta.get_field("author")

        # Assert
        assert field.remote_field.on_delete is models.CASCADE

    def test_author_related_name(self) -> None:
        # Arrange & Act
        field = Book._meta.get_field("author")

        # Assert
        assert field.remote_field.related_name == "books"

    def test_created_at_auto_now_add(self) -> None:
        # Arrange & Act
        field = Book._meta.get_field("created_at")

        # Assert
        assert field.auto_now_add is True
