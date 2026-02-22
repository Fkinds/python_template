import libcst as cst
from fixit import Invalid
from fixit import LintRule
from fixit import Valid

_SELF_NAMES = frozenset({"self", "cls"})


class ParamLineBreak(LintRule):
    """
    Enforce line break conventions for function parameters.

    When a function has one effective parameter (excluding ``self``/``cls``),
    the parameter list should stay on a single line.
    When there are two or more effective parameters, line breaks are required.
    """

    MESSAGE_COLLAPSE = (
        "Single effective parameter should be on one line."
    )
    MESSAGE_EXPAND = (
        "Multiple effective parameters should use line breaks."
    )
    MESSAGE = MESSAGE_COLLAPSE

    VALID = [
        Valid("def f(x: int) -> None: ...\n"),
        Valid(
            "class Foo:\n"
            "    def method(self, x: int) -> None: ...\n"
        ),
        Valid(
            "def f(\n"
            "    x: int,\n"
            "    y: int,\n"
            ") -> None: ...\n"
        ),
        Valid(
            "class Foo:\n"
            "    def method(\n"
            "        self,\n"
            "        x: int,\n"
            "        y: int,\n"
            "    ) -> None: ...\n"
        ),
        Valid("def f() -> None: ...\n"),
        Valid(
            "class Foo:\n"
            "    def method(self) -> None: ...\n"
        ),
    ]

    INVALID = [
        Invalid(
            "def f(\n"
            "    x: int,\n"
            ") -> None: ...\n",
            expected_message=MESSAGE_COLLAPSE,
        ),
        Invalid(
            "class Foo:\n"
            "    def method(\n"
            "        self,\n"
            "        x: int,\n"
            "    ) -> None: ...\n",
            expected_message=MESSAGE_COLLAPSE,
        ),
        Invalid(
            "def f(x: int, y: int) -> None: ...\n",
            expected_message=MESSAGE_EXPAND,
        ),
        Invalid(
            "class Foo:\n"
            "    def method(self, x: int, y: int) -> None: ...\n",
            expected_message=MESSAGE_EXPAND,
        ),
    ]

    def _count_effective_params(self, params: cst.Parameters) -> int:
        total = (
            len(params.posonly_params)
            + len(params.params)
            + (1 if isinstance(params.star_arg, cst.Param) else 0)
            + len(params.kwonly_params)
            + (1 if params.star_kwarg is not None else 0)
        )

        first_params = params.posonly_params or params.params
        if first_params:
            first = first_params[0]
            if (
                isinstance(first.name, cst.Name)
                and first.name.value in _SELF_NAMES
            ):
                total -= 1

        return total

    def _has_newline_in_params(self, node: cst.FunctionDef) -> bool:
        return isinstance(
            node.whitespace_before_params, cst.ParenthesizedWhitespace
        )

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        effective = self._count_effective_params(node.params)
        if effective <= 0:
            return

        has_newline = self._has_newline_in_params(node)

        if effective <= 1 and has_newline:
            self.report(node, self.MESSAGE_COLLAPSE)
        elif effective >= 2 and not has_newline:
            self.report(node, self.MESSAGE_EXPAND)
