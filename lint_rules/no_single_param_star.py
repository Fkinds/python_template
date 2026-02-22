import libcst as cst
from fixit import Invalid
from fixit import LintRule
from fixit import Valid


class NoSingleParamStar(LintRule):
    """
    Prohibit bare ``*`` when there is only one keyword-only param.

    When a function has a single parameter (besides self/cls),
    forcing keyword-only via ``*`` is noise — there is no
    positional ambiguity to prevent.
    """

    MESSAGE = (
        "Remove `*` from single-parameter definition. "
        "Keyword-only marker is redundant with one parameter."
    )

    VALID = [
        Valid("def foo(self, a: int) -> None: ..."),
        Valid(
            "def foo(self, *, a: int, b: str)"
            " -> None: ..."
        ),
        Valid(
            "def foo(a: int, *, b: str) -> None: ..."
        ),
        Valid("def foo(*args: int) -> None: ..."),
    ]

    INVALID = [
        Invalid(
            "def foo(self, *, msg: str) -> None: ..."
        ),
        Invalid(
            "def foo(*, msg: str) -> None: ..."
        ),
    ]

    def visit_FunctionDef(
        self,
        node: cst.FunctionDef,
    ) -> None:
        params = node.params

        # bare * のみ対象 (*args は除外)
        if not isinstance(params.star_arg, cst.ParamStar):
            return

        # kw-only パラメータが2つ以上 → * に意味がある
        if len(params.kwonly_params) != 1:
            return

        # self/cls 以外の positional パラメータがある → * に意味がある
        regular = params.params
        if len(regular) == 0:
            self.report(node)
        elif (
            len(regular) == 1
            and isinstance(regular[0].name, cst.Name)
            and regular[0].name.value in ("self", "cls")
        ):
            self.report(node)
