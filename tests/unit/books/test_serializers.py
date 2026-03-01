import pytest
from rest_framework.exceptions import ValidationError

from books.serializers import BookSerializer


class TestBookSerializerValidateTitle:
    """validate_title の正常系・異常系"""

    def _validate(self, title: str) -> str:
        s = BookSerializer()
        return s.validate_title(title)

    @pytest.mark.parametrize(
        "title",
        ["吾輩は猫である", "Clean Code", "Python入門"],
        ids=["japanese", "english", "mixed"],
    )
    def test_happy_valid_title_accepted(self, title: str) -> None:
        """正常系: 有効なタイトルが受け入れられること."""
        assert self._validate(title) == title

    @pytest.mark.parametrize(
        "title",
        [
            "テスト😀",
            "<script>alert('xss')</script>",
            "",
        ],
        ids=["emoji", "script_tag", "empty"],
    )
    def test_error_invalid_title_rejected(self, title: str) -> None:
        """異常系: 不正なタイトルが拒否されること."""
        with pytest.raises(ValidationError):
            self._validate(title)
