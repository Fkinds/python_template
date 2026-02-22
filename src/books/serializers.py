from rest_framework import serializers

from authors.serializers import AuthorSerializer
from books.entities import TITLE_MAX_LENGTH
from books.entities import TITLE_MIN_LENGTH
from books.entities import Book
from books.entities.safe_text import SafeText


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

    def validate_title(self, value: str) -> str:
        try:
            SafeText(
                value=value,
                min_length=TITLE_MIN_LENGTH,
                max_length=TITLE_MAX_LENGTH,
            )
        except ValueError as e:
            raise serializers.ValidationError(str(e)) from e
        return value


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
