from hypothesis import given
from hypothesis import strategies as st

from books.models import Author
from books.models import Book


class TestAuthor:
    def test_str(self) -> None:
        author = Author(name="夏目漱石")
        assert str(author) == "夏目漱石"

    @given(name=st.text(min_size=1, max_size=255))
    def test_str_returns_name(self, name: str) -> None:
        assert str(Author(name=name)) == name

    def test_str_empty_name(self) -> None:
        assert str(Author(name="")) == ""

    def test_meta_ordering(self) -> None:
        assert Author._meta.ordering == ["name"]

    def test_name_max_length(self) -> None:
        field = Author._meta.get_field("name")
        assert field.max_length == 255

    def test_bio_blank_allowed(self) -> None:
        field = Author._meta.get_field("bio")
        assert field.blank is True

    def test_bio_default_empty(self) -> None:
        field = Author._meta.get_field("bio")
        assert field.default == ""

    def test_created_at_auto_now_add(self) -> None:
        field = Author._meta.get_field("created_at")
        assert field.auto_now_add is True


class TestBook:
    def test_str(self) -> None:
        book = Book(title="吾輩は猫である")
        assert str(book) == "吾輩は猫である"

    @given(title=st.text(min_size=1, max_size=255))
    def test_str_returns_title(self, title: str) -> None:
        assert str(Book(title=title)) == title

    def test_str_empty_title(self) -> None:
        assert str(Book(title="")) == ""

    def test_meta_ordering(self) -> None:
        assert Book._meta.ordering == ["-published_date"]

    def test_expected_fields_exist(self) -> None:
        field_names = {f.name for f in Book._meta.get_fields()}
        expected = {
            "title",
            "isbn",
            "published_date",
            "author",
            "created_at",
        }
        assert expected <= field_names

    def test_title_max_length(self) -> None:
        field = Book._meta.get_field("title")
        assert field.max_length == 255

    def test_isbn_max_length(self) -> None:
        field = Book._meta.get_field("isbn")
        assert field.max_length == 13

    def test_isbn_unique(self) -> None:
        field = Book._meta.get_field("isbn")
        assert field.unique is True

    def test_author_cascade_delete(self) -> None:
        from django.db import models

        field = Book._meta.get_field("author")
        assert field.remote_field.on_delete is models.CASCADE

    def test_author_related_name(self) -> None:
        field = Book._meta.get_field("author")
        assert field.remote_field.related_name == "books"

    def test_created_at_auto_now_add(self) -> None:
        field = Book._meta.get_field("created_at")
        assert field.auto_now_add is True
