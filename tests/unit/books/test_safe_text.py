import pytest
from hypothesis import given
from hypothesis import strategies as st

from books.entities.safe_text import SafeText


class TestSafeTextValid:
    """正常系: 許可されるテキスト"""

    @pytest.mark.parametrize(
        "text",
        [
            "ひらがな",
            "カタカナ",
            "漢字",
            "Hello World",
            "Python入門",
            "C++ Programming: A Guide",
            "吾輩は猫である。",
            "C(改訂版)",
            "吾輩は\u3000猫である",
        ],
        ids=[
            "hiragana",
            "katakana",
            "kanji",
            "english",
            "mixed_ja_en",
            "ascii_punct",
            "fullwidth_punct",
            "parentheses",
            "fullwidth_space",
        ],
    )
    def test_happy_accepts_valid_text(self, text: str) -> None:
        """正常系: 許可される各種テキストが受け入れられること."""
        # Arrange & Act
        vo = SafeText(value=text)

        # Assert
        assert vo.value == text

    def test_happy_min_boundary_one_char(self) -> None:
        vo = SafeText(value="a")
        assert vo.value == "a"

    def test_happy_max_boundary_255_chars(self) -> None:
        text = "a" * 255
        vo = SafeText(value=text)
        assert vo.value == text

    def test_happy_custom_min_max_length(self) -> None:
        vo = SafeText(value="abc", min_length=3, max_length=10)
        assert vo.value == "abc"

    def test_happy_frozen_immutability(self) -> None:
        vo = SafeText(value="テスト")
        with pytest.raises(AttributeError):
            vo.value = "変更"  # type: ignore[misc]

    def test_happy_equality_by_value(self) -> None:
        vo1 = SafeText(value="テスト")
        vo2 = SafeText(value="テスト")
        assert vo1 == vo2

    def test_happy_inequality_by_value(self) -> None:
        vo1 = SafeText(value="テストA")
        vo2 = SafeText(value="テストB")
        assert vo1 != vo2

    @given(
        text=st.text(
            min_size=1,
            max_size=255,
            alphabet=st.characters(
                whitelist_categories=("L", "N", "Zs"),
                whitelist_characters=(
                    "\u3000-\u303f\u30fc\u30fb"
                    "\u3001\u3002\uff01\uff1f"
                    "-,.!?'\"()&+:;/ \t"
                ),
            ),
        ).filter(lambda s: s.strip())
    )
    def test_happy_accepts_any_safe_text(self, text: str) -> None:
        """正常系: 許可パターンに合致する任意テキストが受け入れられること."""
        # Arrange & Act
        vo = SafeText(value=text)

        # Assert
        assert vo.value == text


class TestSafeTextInvalid:
    """異常系: 拒否されるテキスト"""

    def test_error_empty_string(self) -> None:
        with pytest.raises(ValueError, match="1文字以上"):
            SafeText(value="")

    def test_error_exceeds_max_length(self) -> None:
        with pytest.raises(ValueError, match="255文字以下"):
            SafeText(value="a" * 256)

    def test_error_custom_min_length_violation(
        self,
    ) -> None:
        with pytest.raises(ValueError, match="3文字以上"):
            SafeText(value="ab", min_length=3)

    def test_error_custom_max_length_violation(
        self,
    ) -> None:
        with pytest.raises(ValueError, match="5文字以下"):
            SafeText(value="abcdef", max_length=5)

    @pytest.mark.parametrize(
        "text",
        [
            "テスト😀",
            "<script>alert('xss')</script>",
            "test<>value",
            "test{value}",
            "test`cmd`",
            "test\x00value",
            "test\x07value",
        ],
        ids=[
            "emoji",
            "script_tag",
            "angle_brackets",
            "curly_braces",
            "backtick",
            "null_byte",
            "control_char",
        ],
    )
    def test_error_rejects_unsafe_chars(self, text: str) -> None:
        """異常系: 禁止文字を含むテキストが拒否されること."""
        with pytest.raises(ValueError, match="使用できない文字"):
            SafeText(value=text)

    def test_error_positional_args_rejected(self) -> None:
        with pytest.raises(TypeError):
            SafeText("テスト")  # type: ignore[misc]  # lint-ignore: NoPositionalArgs

    @given(
        text=st.text(
            min_size=1,
            max_size=255,
            alphabet=st.characters(
                whitelist_categories=("So", "Sk"),
            ),
        )
    )
    def test_error_rejects_any_unsafe_text(self, text: str) -> None:
        """異常系: 記号カテゴリの任意テキストが拒否されること."""
        with pytest.raises(ValueError, match="使用できない文字"):
            SafeText(value=text)
