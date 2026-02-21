from hypothesis import given
from hypothesis import strategies as st

from books.serializers import AuthorSerializer
from books.serializers import BookDetailSerializer
from books.serializers import BookSerializer


# AuthorSerializer は unique/FK が無いため is_valid() が DB 不要
class TestAuthorSerializer:
    def test_meta_fields(self) -> None:
        # Arrange & Act
        fields = AuthorSerializer.Meta.fields

        # Assert
        assert fields == [
            "id",
            "name",
            "bio",
            "created_at",
        ]

    def test_read_only_fields(self) -> None:
        # Arrange & Act
        read_only = AuthorSerializer.Meta.read_only_fields

        # Assert
        assert read_only == [
            "id",
            "created_at",
        ]

    # --- 正常系 ---

    def test_valid_with_name_only(self) -> None:
        # Arrange
        data = {"name": "太宰治"}

        # Act
        s = AuthorSerializer(data=data)

        # Assert
        assert s.is_valid()

    def test_valid_with_name_and_bio(self) -> None:
        # Arrange
        data = {
            "name": "太宰治",
            "bio": "走れメロスの著者",
        }

        # Act
        s = AuthorSerializer(data=data)

        # Assert
        assert s.is_valid()

    def test_valid_with_empty_bio(self) -> None:
        # Arrange
        data = {"name": "太宰治", "bio": ""}

        # Act
        s = AuthorSerializer(data=data)

        # Assert
        assert s.is_valid()

    @given(
        name=st.text(
            min_size=1,
            max_size=255,
            alphabet=st.characters(
                blacklist_categories=("Cs",),
                blacklist_characters="\x00",
            ),
        ).filter(lambda s: s.strip())
    )
    def test_valid_any_name(self, name: str) -> None:
        # Arrange
        data = {"name": name}

        # Act
        s = AuthorSerializer(data=data)

        # Assert
        assert s.is_valid(), s.errors

    def test_whitespace_only_name_rejected(self) -> None:
        for ws in (" ", "\t", "\r", "\n", "  \t\n"):
            # Arrange
            data = {"name": ws}

            # Act
            s = AuthorSerializer(data=data)

            # Assert
            assert not s.is_valid()

    def test_name_exactly_max_length(self) -> None:
        # Arrange
        data = {"name": "a" * 255}

        # Act
        s = AuthorSerializer(data=data)

        # Assert
        assert s.is_valid()

    def test_read_only_id_ignored(self) -> None:
        # Arrange
        data = {"id": 999, "name": "テスト"}

        # Act
        s = AuthorSerializer(data=data)

        # Assert
        assert s.is_valid()
        assert "id" not in s.validated_data

    # --- 異常系 ---

    def test_missing_name(self) -> None:
        # Arrange
        data = {"bio": "略歴"}

        # Act
        s = AuthorSerializer(data=data)

        # Assert
        assert not s.is_valid()
        assert "name" in s.errors

    def test_empty_data(self) -> None:
        # Arrange
        data: dict[str, str] = {}

        # Act
        s = AuthorSerializer(data=data)

        # Assert
        assert not s.is_valid()
        assert "name" in s.errors

    def test_name_over_max_length(self) -> None:
        # Arrange
        data = {"name": "a" * 256}

        # Act
        s = AuthorSerializer(data=data)

        # Assert
        assert not s.is_valid()
        assert "name" in s.errors

    @given(
        name=st.text(
            min_size=256,
            max_size=500,
            alphabet=st.characters(
                blacklist_categories=("Cs",),
                blacklist_characters="\x00",
            ),
        )
    )
    def test_long_name_rejected(self, name: str) -> None:
        # Arrange
        data = {"name": name}

        # Act
        s = AuthorSerializer(data=data)

        # Assert
        assert not s.is_valid()
        assert "name" in s.errors

    def test_null_char_in_name(self) -> None:
        # Arrange
        data = {"name": "a\x00b"}

        # Act
        s = AuthorSerializer(data=data)

        # Assert
        assert not s.is_valid()


# BookSerializer は isbn unique / author FK で DB アクセスするため
# is_valid() は unit テストで使えない。Meta 定義と個別フィールドのみテスト
class TestBookSerializer:
    def test_meta_fields(self) -> None:
        # Arrange & Act
        fields = BookSerializer.Meta.fields

        # Assert
        assert fields == [
            "id",
            "title",
            "isbn",
            "published_date",
            "author",
            "created_at",
        ]

    def test_read_only_fields(self) -> None:
        # Arrange & Act
        read_only = BookSerializer.Meta.read_only_fields

        # Assert
        assert read_only == [
            "id",
            "created_at",
        ]

    def test_id_is_read_only(self) -> None:
        # Arrange & Act
        read_only = BookSerializer.Meta.read_only_fields

        # Assert
        assert "id" in read_only

    def test_created_at_is_read_only(self) -> None:
        # Arrange & Act
        read_only = BookSerializer.Meta.read_only_fields

        # Assert
        assert "created_at" in read_only

    def test_required_fields(self) -> None:
        # Arrange
        s = BookSerializer()

        # Act
        required = {name for name, field in s.fields.items() if field.required}

        # Assert
        assert {"title", "isbn", "published_date", "author"} == required

    def test_title_max_length(self) -> None:
        # Arrange
        s = BookSerializer()

        # Act
        max_length = s.fields["title"].max_length

        # Assert
        assert max_length == 255

    def test_isbn_max_length(self) -> None:
        # Arrange
        s = BookSerializer()

        # Act
        max_length = s.fields["isbn"].max_length

        # Assert
        assert max_length == 13


class TestBookDetailSerializer:
    def test_meta_fields(self) -> None:
        # Arrange & Act
        fields = BookDetailSerializer.Meta.fields

        # Assert
        assert fields == [
            "id",
            "title",
            "isbn",
            "published_date",
            "author",
            "created_at",
        ]

    def test_author_is_nested(self) -> None:
        # Arrange
        s = BookDetailSerializer()

        # Act
        author_field = s.fields["author"]

        # Assert
        assert isinstance(author_field, AuthorSerializer)

    def test_author_is_read_only(self) -> None:
        # Arrange
        s = BookDetailSerializer()

        # Act
        author_field = s.fields["author"]

        # Assert
        assert author_field.read_only is True
