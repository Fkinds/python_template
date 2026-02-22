import pytest
from rest_framework.exceptions import ValidationError

from authors.serializers import AuthorSerializer
from books.serializers import BookDetailSerializer
from books.serializers import BookSerializer


# BookSerializer は isbn unique / author FK で DB アクセスするため
# is_valid() は unit テストで使えない。Meta 定義と個別フィールドのみテスト
class TestBookSerializer:
    def test_happy_exposes_expected_fields(self) -> None:
        # Arrange & Act
        s = BookSerializer()

        # Assert
        assert set(s.fields.keys()) == {
            "id",
            "title",
            "isbn",
            "published_date",
            "author",
            "cover_image",
            "created_at",
        }

    def test_happy_id_and_created_at_are_read_only(self) -> None:
        # Arrange & Act
        s = BookSerializer()

        # Assert
        assert s.fields["id"].read_only
        assert s.fields["created_at"].read_only

    def test_happy_requires_title_isbn_date_author(self) -> None:
        # Arrange
        s = BookSerializer()

        # Act
        required = {name for name, field in s.fields.items() if field.required}

        # Assert
        assert {"title", "isbn", "published_date", "author"} == required

    def test_happy_title_max_length_is_255(self) -> None:
        # Arrange
        s = BookSerializer()

        # Act
        max_length = s.fields["title"].max_length

        # Assert
        assert max_length == 255

    def test_happy_isbn_max_length_is_13(self) -> None:
        # Arrange
        s = BookSerializer()

        # Act
        max_length = s.fields["isbn"].max_length

        # Assert
        assert max_length == 13


class TestBookSerializerValidateTitle:
    """validate_title の正常系・異常系"""

    def _validate(self, title: str) -> str:
        s = BookSerializer()
        return s.validate_title(title)

    def test_happy_japanese_title(self) -> None:
        assert self._validate("吾輩は猫である") == "吾輩は猫である"

    def test_happy_english_title(self) -> None:
        assert self._validate("Clean Code") == "Clean Code"

    def test_happy_mixed_title(self) -> None:
        assert self._validate("Python入門") == "Python入門"

    def test_error_emoji_rejected(self) -> None:
        with pytest.raises(ValidationError):
            self._validate("テスト😀")

    def test_error_script_tag_rejected(self) -> None:
        with pytest.raises(ValidationError):
            self._validate("<script>alert('xss')</script>")

    def test_error_empty_string_rejected(self) -> None:
        with pytest.raises(ValidationError):
            self._validate("")


class TestBookDetailSerializer:
    def test_happy_exposes_expected_fields(self) -> None:
        # Arrange & Act
        s = BookDetailSerializer()

        # Assert
        assert set(s.fields.keys()) == {
            "id",
            "title",
            "isbn",
            "published_date",
            "author",
            "cover_image",
            "created_at",
        }

    def test_happy_nests_author_as_serializer(self) -> None:
        # Arrange
        s = BookDetailSerializer()

        # Act
        author_field = s.fields["author"]

        # Assert
        assert isinstance(author_field, AuthorSerializer)

    def test_happy_author_is_read_only(self) -> None:
        # Arrange
        s = BookDetailSerializer()

        # Act
        author_field = s.fields["author"]

        # Assert
        assert author_field.read_only is True
