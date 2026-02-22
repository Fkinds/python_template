import pytest
from hypothesis import given
from hypothesis import strategies as st

from authors.serializers import AuthorSerializer


# AuthorSerializer は unique/FK が無いため is_valid() が DB 不要
class TestAuthorSerializer:
    # --- 正常系 ---

    def test_happy_exposes_expected_fields(self) -> None:
        # Arrange & Act
        s = AuthorSerializer()

        # Assert
        assert set(s.fields.keys()) == {"id", "name", "bio", "created_at"}

    def test_happy_id_and_created_at_are_read_only(self) -> None:
        # Arrange & Act
        s = AuthorSerializer()

        # Assert
        assert s.fields["id"].read_only
        assert s.fields["created_at"].read_only

    def test_happy_accepts_name_only(self) -> None:
        # Arrange
        data = {"name": "太宰治"}

        # Act
        s = AuthorSerializer(data=data)

        # Assert
        assert s.is_valid()

    def test_happy_accepts_name_and_bio(self) -> None:
        # Arrange
        data = {
            "name": "太宰治",
            "bio": "走れメロスの著者",
        }

        # Act
        s = AuthorSerializer(data=data)

        # Assert
        assert s.is_valid()

    def test_happy_accepts_empty_bio(self) -> None:
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
    def test_happy_accepts_any_valid_name(self, name: str) -> None:
        # Arrange
        data = {"name": name}

        # Act
        s = AuthorSerializer(data=data)

        # Assert
        assert s.is_valid(), s.errors

    def test_happy_accepts_name_at_max_length(self) -> None:
        # Arrange
        data = {"name": "a" * 255}

        # Act
        s = AuthorSerializer(data=data)

        # Assert
        assert s.is_valid()

    def test_happy_ignores_id_in_input(self) -> None:
        # Arrange
        data = {"id": 999, "name": "テスト"}

        # Act
        s = AuthorSerializer(data=data)

        # Assert
        assert s.is_valid()
        assert "id" not in s.validated_data

    # --- 異常系 ---

    @pytest.mark.parametrize(
        "ws",
        [" ", "\t", "\r", "\n", "  \t\n"],
        ids=["space", "tab", "cr", "lf", "mixed"],
    )
    def test_error_rejects_whitespace_only_name(self, ws: str) -> None:
        """異常系: 空白のみの名前が拒否されること."""
        # Arrange
        data = {"name": ws}

        # Act
        s = AuthorSerializer(data=data)

        # Assert
        assert not s.is_valid()

    def test_error_rejects_missing_name(self) -> None:
        # Arrange
        data = {"bio": "略歴"}

        # Act
        s = AuthorSerializer(data=data)

        # Assert
        assert not s.is_valid()
        assert "name" in s.errors

    def test_error_rejects_empty_data(self) -> None:
        # Arrange
        data: dict[str, str] = {}

        # Act
        s = AuthorSerializer(data=data)

        # Assert
        assert not s.is_valid()
        assert "name" in s.errors

    def test_error_rejects_name_over_max_length(self) -> None:
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
        ).filter(lambda s: len(s.strip()) > 255)
    )
    def test_error_rejects_long_name(self, name: str) -> None:
        # Arrange
        data = {"name": name}

        # Act
        s = AuthorSerializer(data=data)

        # Assert
        assert not s.is_valid()
        assert "name" in s.errors

    def test_error_rejects_null_char_in_name(self) -> None:
        # Arrange
        data = {"name": "a\x00b"}

        # Act
        s = AuthorSerializer(data=data)

        # Assert
        assert not s.is_valid()
