import libcst as cst
import libcst.matchers as m
from fixit import Invalid
from fixit import LintRule
from fixit import Valid


class NoAttrShorthand(LintRule):
    """
    Prohibit the legacy ``attr`` module in favor of ``attrs``.

    The old shorthand ``import attr`` / ``from attr import …``
    exposes deprecated APIs (``attr.s``, ``attr.ib``, etc.).
    Always use ``import attrs`` and its modern API instead.
    """

    MESSAGE = (
        "Use `import attrs` instead of `import attr`. "
        "The `attr` shorthand exposes deprecated APIs."
    )

    VALID = [
        Valid("import attrs"),
        Valid("from attrs import frozen"),
        Valid("from attrs.validators import instance_of"),
        Valid("import json"),
        Valid("from collections import OrderedDict"),
    ]

    INVALID = [
        Invalid("import attr"),
        Invalid("from attr import s"),
        Invalid("from attr import attrib"),
        Invalid("from attr.validators import instance_of"),
    ]

    def _is_attr_name(self, node: cst.BaseExpression) -> bool:
        """Return True for ``attr`` or ``attr.xxx``."""
        if m.matches(node, m.Name("attr")):
            return True
        return m.matches(
            node,
            m.Attribute(value=m.Name("attr")),
        )

    def visit_Import(self, node: cst.Import) -> None:
        if isinstance(node.names, cst.ImportStar):
            return
        for alias in node.names:
            if self._is_attr_name(alias.name):
                self.report(node)
                return

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        if node.module is None:
            return
        if self._is_attr_name(node.module):
            self.report(node)
