import libcst as cst
import libcst.matchers as m
from fixit import Invalid
from fixit import LintRule
from fixit import Valid


class AttrsKwOnly(LintRule):
    """
    Enforce ``kw_only=True`` on attrs frozen classes.

    All ``@attrs.frozen`` classes should use keyword-only arguments
    to prevent positional instantiation mistakes.
    """

    MESSAGE = (
        "`@attrs.frozen` should use `kw_only=True` to enforce "
        "keyword-only arguments."
    )

    VALID = [
        Valid(
            "import attrs\n"
            "@attrs.frozen(kw_only=True)\n"
            "class Foo:\n"
            "    x: int = 1\n"
        ),
        Valid(
            "import attrs\n"
            "@attrs.define(kw_only=True)\n"
            "class Foo:\n"
            "    x: int = 1\n"
        ),
        Valid(
            "from dataclasses import dataclass\n"
            "@dataclass\n"
            "class Foo:\n"
            "    x: int = 1\n"
        ),
    ]

    INVALID = [
        Invalid("import attrs\n@attrs.frozen\nclass Foo:\n    x: int = 1\n"),
        Invalid("import attrs\n@attrs.frozen()\nclass Foo:\n    x: int = 1\n"),
        Invalid("import attrs\n@attrs.define\nclass Foo:\n    x: int = 1\n"),
        Invalid("import attrs\n@attrs.define()\nclass Foo:\n    x: int = 1\n"),
    ]

    _ATTRS_DECORATORS = {"frozen", "define"}

    def _is_attrs_decorator(self, node: cst.BaseExpression) -> bool:
        # @attrs.frozen / @attrs.define
        if m.matches(
            node,
            m.Attribute(
                value=m.Name("attrs"),
                attr=m.Name(),
            ),
        ):
            attr_node = cst.ensure_type(node, cst.Attribute)
            return attr_node.attr.value in self._ATTRS_DECORATORS
        return False

    def _has_kw_only(self, node: cst.Call) -> bool:
        for arg in node.args:
            if m.matches(
                arg,
                m.Arg(
                    keyword=m.Name("kw_only"),
                    value=m.Name("True"),
                ),
            ):
                return True
        return False

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        for decorator in node.decorators:
            dec = decorator.decorator

            # @attrs.frozen / @attrs.define (no parentheses)
            if self._is_attrs_decorator(dec):
                self.report(node)
                return

            # @attrs.frozen(...) / @attrs.define(...)
            if m.matches(dec, m.Call()):
                call = cst.ensure_type(dec, cst.Call)
                if self._is_attrs_decorator(
                    call.func,
                ) and not self._has_kw_only(call):
                    self.report(node)
                    return
