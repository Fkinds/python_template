from rest_framework import serializers

from authors.serializers import AuthorSerializer
from books.models import Book


class BookSerializer(serializers.ModelSerializer[Book]):
    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "isbn",
            "published_date",
            "author",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class BookDetailSerializer(serializers.ModelSerializer[Book]):
    """読み取り用: author をネストして返す."""

    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "isbn",
            "published_date",
            "author",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
