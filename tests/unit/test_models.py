import datetime

import pytest

from books.models import Author
from books.models import Book


@pytest.mark.django_db
class TestAuthor:
    def test_str(self, author: Author) -> None:
        assert str(author) == "夏目漱石"

    def test_ordering(self, db: None) -> None:
        Author.objects.create(name="太宰治")
        Author.objects.create(name="夏目漱石")
        names = list(Author.objects.values_list("name", flat=True))
        assert names == ["夏目漱石", "太宰治"]


@pytest.mark.django_db
class TestBook:
    def test_str(self, book: Book) -> None:
        assert str(book) == "吾輩は猫である"

    def test_author_relation(self, book: Book) -> None:
        assert book.author.name == "夏目漱石"
        assert book.author.books.count() == 1

    def test_ordering(self, author: Author) -> None:
        Book.objects.create(
            title="旧作",
            isbn="1111111111111",
            published_date=datetime.date(1900, 1, 1),
            author=author,
        )
        Book.objects.create(
            title="新作",
            isbn="2222222222222",
            published_date=datetime.date(2000, 1, 1),
            author=author,
        )
        titles = list(Book.objects.values_list("title", flat=True))
        assert titles == ["新作", "旧作"]
