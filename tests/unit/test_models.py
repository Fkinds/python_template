from books.models import Author
from books.models import Book


class TestAuthor:
    def test_str(self) -> None:
        author = Author(name="夏目漱石")
        assert str(author) == "夏目漱石"

    def test_meta_ordering(self) -> None:
        assert Author._meta.ordering == ["name"]


class TestBook:
    def test_str(self) -> None:
        book = Book(title="吾輩は猫である")
        assert str(book) == "吾輩は猫である"

    def test_meta_ordering(self) -> None:
        assert Book._meta.ordering == ["-published_date"]

    def test_fields(self) -> None:
        field_names = {f.name for f in Book._meta.get_fields()}
        assert {"title", "isbn", "published_date", "author"} <= field_names
