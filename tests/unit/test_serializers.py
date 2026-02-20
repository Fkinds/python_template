import pytest

from books.models import Author
from books.models import Book
from books.serializers import AuthorSerializer
from books.serializers import BookDetailSerializer
from books.serializers import BookSerializer


@pytest.mark.django_db
class TestAuthorSerializer:
    def test_fields(self, author: Author) -> None:
        data = AuthorSerializer(author).data
        assert set(data.keys()) == {"id", "name", "bio", "created_at"}

    def test_create(self, db: None) -> None:
        serializer = AuthorSerializer(
            data={"name": "太宰治", "bio": "走れメロスの著者"}
        )
        assert serializer.is_valid()
        obj = serializer.save()
        assert obj.name == "太宰治"


@pytest.mark.django_db
class TestBookSerializer:
    def test_fields(self, book: Book) -> None:
        data = BookSerializer(book).data
        assert set(data.keys()) == {
            "id",
            "title",
            "isbn",
            "published_date",
            "author",
            "created_at",
        }
        assert data["author"] == book.author.pk

    def test_create(self, author: Author) -> None:
        serializer = BookSerializer(
            data={
                "title": "坊っちゃん",
                "isbn": "9784003101025",
                "published_date": "1906-04-01",
                "author": author.pk,
            }
        )
        assert serializer.is_valid(), serializer.errors
        obj = serializer.save()
        assert obj.title == "坊っちゃん"

    def test_duplicate_isbn(self, book: Book) -> None:
        serializer = BookSerializer(
            data={
                "title": "重複",
                "isbn": book.isbn,
                "published_date": "2000-01-01",
                "author": book.author.pk,
            }
        )
        assert not serializer.is_valid()
        assert "isbn" in serializer.errors


@pytest.mark.django_db
class TestBookDetailSerializer:
    def test_nested_author(self, book: Book) -> None:
        data = BookDetailSerializer(book).data
        assert isinstance(data["author"], dict)
        assert data["author"]["name"] == "夏目漱石"
