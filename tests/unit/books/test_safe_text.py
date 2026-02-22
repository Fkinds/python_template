import pytest

from books.entities.safe_text import SafeText


class TestSafeTextValid:
    """正常系: 許可されるテキスト"""

    def test_japanese_hiragana(self) -> None:
        vo = SafeText(value="ひらがな")
        assert vo.value == "ひらがな"

    def test_japanese_katakana(self) -> None:
        vo = SafeText(value="カタカナ")
        assert vo.value == "カタカナ"

    def test_japanese_kanji(self) -> None:
        vo = SafeText(value="漢字")
        assert vo.value == "漢字"

    def test_english(self) -> None:
        vo = SafeText(value="Hello World")
        assert vo.value == "Hello World"

    def test_mixed_japanese_english(self) -> None:
        vo = SafeText(value="Python入門")
        assert vo.value == "Python入門"

    def test_ascii_punctuation(self) -> None:
        vo = SafeText(value="C++ Programming: A Guide")
        assert vo.value == "C++ Programming: A Guide"

    def test_fullwidth_punctuation(self) -> None:
        vo = SafeText(value="吾輩は猫である。")
        assert vo.value == "吾輩は猫である。"

    def test_parentheses_and_symbols(self) -> None:
        vo = SafeText(value="C(改訂版)")
        assert vo.value == "C(改訂版)"

    def test_min_boundary_one_char(self) -> None:
        vo = SafeText(value="a")
        assert vo.value == "a"

    def test_max_boundary_255_chars(self) -> None:
        text = "a" * 255
        vo = SafeText(value=text)
        assert vo.value == text

    def test_custom_min_max_length(self) -> None:
        vo = SafeText(value="abc", min_length=3, max_length=10)
        assert vo.value == "abc"

    def test_fullwidth_space(self) -> None:
        vo = SafeText(value="吾輩は\u3000猫である")
        assert vo.value == "吾輩は\u3000猫である"

    def test_frozen_immutability(self) -> None:
        vo = SafeText(value="テスト")
        with pytest.raises(AttributeError):
            vo.value = "変更"  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        vo1 = SafeText(value="テスト")
        vo2 = SafeText(value="テスト")
        assert vo1 == vo2

    def test_inequality_by_value(self) -> None:
        vo1 = SafeText(value="テストA")
        vo2 = SafeText(value="テストB")
        assert vo1 != vo2


class TestSafeTextInvalid:
    """異常系: 拒否されるテキスト"""

    def test_empty_string(self) -> None:
        with pytest.raises(ValueError, match="1文字以上"):
            SafeText(value="")

    def test_exceeds_max_length(self) -> None:
        with pytest.raises(ValueError, match="255文字以下"):
            SafeText(value="a" * 256)

    def test_custom_min_length_violation(self) -> None:
        with pytest.raises(ValueError, match="3文字以上"):
            SafeText(value="ab", min_length=3)

    def test_custom_max_length_violation(self) -> None:
        with pytest.raises(ValueError, match="5文字以下"):
            SafeText(value="abcdef", max_length=5)

    def test_emoji(self) -> None:
        with pytest.raises(ValueError, match="使用できない文字"):
            SafeText(value="テスト😀")

    def test_script_tag(self) -> None:
        with pytest.raises(ValueError, match="使用できない文字"):
            SafeText(value="<script>alert('xss')</script>")

    def test_angle_brackets(self) -> None:
        with pytest.raises(ValueError, match="使用できない文字"):
            SafeText(value="test<>value")

    def test_curly_braces(self) -> None:
        with pytest.raises(ValueError, match="使用できない文字"):
            SafeText(value="test{value}")

    def test_backtick(self) -> None:
        with pytest.raises(ValueError, match="使用できない文字"):
            SafeText(value="test`cmd`")

    def test_null_byte(self) -> None:
        with pytest.raises(ValueError, match="使用できない文字"):
            SafeText(value="test\x00value")

    def test_control_characters(self) -> None:
        with pytest.raises(ValueError, match="使用できない文字"):
            SafeText(value="test\x07value")

    def test_positional_args_rejected(self) -> None:
        with pytest.raises(TypeError):
            SafeText("テスト")  # type: ignore[misc]  # lint-ignore: NoPositionalArgs
