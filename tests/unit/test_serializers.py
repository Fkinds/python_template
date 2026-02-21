from hypothesis import given
from hypothesis import strategies as st

from books.serializers import AuthorSerializer
from books.serializers import BookDetailSerializer
from books.serializers import BookSerializer


# AuthorSerializer は unique/FK が無いため is_valid() が DB 不要
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

    # --- 正常系 ---

    def test_valid_with_name_only(self) -> None:
        s = AuthorSerializer(data={"name": "太宰治"})
        assert s.is_valid()

    def test_valid_with_name_and_bio(self) -> None:
        s = AuthorSerializer(
            data={
                "name": "太宰治",
                "bio": "走れメロスの著者",
            }
        )
        assert s.is_valid()

    def test_valid_with_empty_bio(self) -> None:
        s = AuthorSerializer(data={"name": "太宰治", "bio": ""})
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
        s = AuthorSerializer(data={"name": name})
        assert s.is_valid(), s.errors

    def test_whitespace_only_name_rejected(self) -> None:
        for ws in (" ", "\t", "\r", "\n", "  \t\n"):
            s = AuthorSerializer(data={"name": ws})
            assert not s.is_valid()

    def test_name_exactly_max_length(self) -> None:
        s = AuthorSerializer(data={"name": "a" * 255})
        assert s.is_valid()

    def test_read_only_id_ignored(self) -> None:
        s = AuthorSerializer(data={"id": 999, "name": "テスト"})
        assert s.is_valid()
        assert "id" not in s.validated_data

    # --- 異常系 ---

    def test_missing_name(self) -> None:
        s = AuthorSerializer(data={"bio": "略歴"})
        assert not s.is_valid()
        assert "name" in s.errors

    def test_empty_data(self) -> None:
        s = AuthorSerializer(data={})
        assert not s.is_valid()
        assert "name" in s.errors

    def test_name_over_max_length(self) -> None:
        s = AuthorSerializer(data={"name": "a" * 256})
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
        s = AuthorSerializer(data={"name": name})
        assert not s.is_valid()
        assert "name" in s.errors

    def test_null_char_in_name(self) -> None:
        s = AuthorSerializer(data={"name": "a\x00b"})
        assert not s.is_valid()


# BookSerializer は isbn unique / author FK で DB アクセスするため
# is_valid() は unit テストで使えない。Meta 定義と個別フィールドのみテスト
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

    def test_id_is_read_only(self) -> None:
        assert "id" in BookSerializer.Meta.read_only_fields

    def test_created_at_is_read_only(self) -> None:
        assert "created_at" in BookSerializer.Meta.read_only_fields

    def test_required_fields(self) -> None:
        s = BookSerializer()
        required = {name for name, field in s.fields.items() if field.required}
        assert {"title", "isbn", "published_date", "author"} == required

    def test_title_max_length(self) -> None:
        s = BookSerializer()
        assert s.fields["title"].max_length == 255

    def test_isbn_max_length(self) -> None:
        s = BookSerializer()
        assert s.fields["isbn"].max_length == 13


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

    def test_author_is_read_only(self) -> None:
        author_field = BookDetailSerializer().fields["author"]
        assert author_field.read_only is True
