import libcst as cst
from fixit import Invalid
from fixit import LintRule
from fixit import Valid

_FIRST_PARTY_PACKAGES = frozenset(
    {"books", "authors", "config", "notifications"}
)


class NoPositionalArgs(LintRule):
    """
    Prohibit positional arguments in calls to first-party code.

    All calls to functions and classes imported from project modules
    (books, authors, config) must use keyword arguments.
    This does not apply to stdlib or third-party calls.
    """

    MESSAGE = (
        "Use keyword arguments for project code calls. "
        "Positional arguments are not allowed."
    )

    VALID = [
        Valid(
            "from books.entities.safe_text import SafeText\n"
            "SafeText(value='test')\n"
        ),
        Valid("from books.entities import Book\nBook(title='test')\n"),
        Valid("len([1, 2, 3])\n"),
        Valid("print('hello')\n"),
        Valid("range(10)\n"),
    ]

    INVALID = [
        Invalid(
            "from books.entities.safe_text import SafeText\nSafeText('test')\n"
        ),
        Invalid("from books.entities import Book\nBook('test')\n"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._first_party_names: set[str] = set()

    def _get_root_module(self, node: cst.BaseExpression) -> str | None:
        if isinstance(node, cst.Name):
            return node.value
        if isinstance(node, cst.Attribute):
            return self._get_root_module(node.value)
        return None

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        if node.module is None:
            return

        root = self._get_root_module(node.module)
        if root not in _FIRST_PARTY_PACKAGES:
            return

        if isinstance(node.names, cst.ImportStar):
            return

        for alias in node.names:
            if alias.asname and isinstance(alias.asname, cst.AsName):
                asname_node = alias.asname.name
                if isinstance(asname_node, cst.Name):
                    self._first_party_names.add(asname_node.value)
            elif isinstance(alias.name, cst.Name):
                self._first_party_names.add(alias.name.value)

    def _get_call_name(self, node: cst.BaseExpression) -> str | None:
        if isinstance(node, cst.Name):
            return node.value
        return None

    def visit_Call(self, node: cst.Call) -> None:
        name = self._get_call_name(node.func)
        if name is None or name not in self._first_party_names:
            return

        for arg in node.args:
            if arg.keyword is None and arg.star == "":
                self.report(node)
                return
