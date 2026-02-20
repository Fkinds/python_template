from books.serializers import AuthorSerializer
from books.serializers import BookDetailSerializer
from books.serializers import BookSerializer


class TestAuthorSerializer:
    def test_meta_fields(self) -> None:
        assert AuthorSerializer.Meta.fields == [
            "id",
            "name",
            "bio",
            "created_at",
        ]

    def test_read_only_fields(self) -> None:
        assert AuthorSerializer.Meta.read_only_fields == [
            "id",
            "created_at",
        ]

    def test_valid_data(self) -> None:
        serializer = AuthorSerializer(
            data={"name": "太宰治", "bio": "走れメロスの著者"}
        )
        assert serializer.is_valid()

    def test_missing_name(self) -> None:
        serializer = AuthorSerializer(data={"bio": "略歴"})
        assert not serializer.is_valid()
        assert "name" in serializer.errors


class TestBookSerializer:
    def test_meta_fields(self) -> None:
        assert BookSerializer.Meta.fields == [
            "id",
            "title",
            "isbn",
            "published_date",
            "author",
            "created_at",
        ]

    def test_read_only_fields(self) -> None:
        assert BookSerializer.Meta.read_only_fields == [
            "id",
            "created_at",
        ]


class TestBookDetailSerializer:
    def test_meta_fields(self) -> None:
        assert BookDetailSerializer.Meta.fields == [
            "id",
            "title",
            "isbn",
            "published_date",
            "author",
            "created_at",
        ]

    def test_author_is_nested(self) -> None:
        author_field = BookDetailSerializer().fields["author"]
        assert isinstance(author_field, AuthorSerializer)
