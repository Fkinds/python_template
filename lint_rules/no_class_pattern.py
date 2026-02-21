import libcst as cst
from fixit import Invalid
from fixit import LintRule
from fixit import Valid


class NoClassPattern(LintRule):
    """
    Prohibit class patterns in ``match``/``case`` statements.

    Class patterns such as ``case Point(x, y):`` resemble constructor
    calls or variable definitions in other languages, which makes them
    confusing to read.  Prefer using ``case`` with ``if`` guards or
    ``isinstance()`` checks instead.
    """

    MESSAGE = (
        "Do not use class patterns in `match`/`case`. "
        "They look like constructor calls and are easy to misread. "
        "Use `isinstance()` or guard expressions instead."
    )

    VALID = [
        Valid('match command:\n    case "quit":\n        quit()\n'),
        Valid("match point:\n    case (x, y):\n        print(x, y)\n"),
        Valid("match value:\n    case 1 | 2 | 3:\n        print('small')\n"),
        Valid(
            'match mapping:\n    case {"key": value}:\n        print(value)\n'
        ),
    ]

    INVALID = [
        Invalid("match point:\n    case Point(x, y):\n        print(x, y)\n"),
        Invalid(
            "match color:\n"
            '    case Color(name="red"):\n'
            "        print('red')\n"
        ),
        Invalid(
            "match event:\n"
            "    case Click(position=(x, y)):\n"
            "        handle(x, y)\n"
        ),
    ]

    def visit_MatchClass(self, node: cst.MatchClass) -> None:
        self.report(node)
