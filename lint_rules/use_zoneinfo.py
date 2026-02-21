import libcst as cst
import libcst.matchers as m
from fixit import Invalid
from fixit import LintRule
from fixit import Valid


class UseZoneInfo(LintRule):
    """
    Detect usage of ``datetime.timezone.utc``, ``pytz``, or
    ``dateutil.tz`` and suggest ``zoneinfo.ZoneInfo`` instead.

    Since Python 3.9, ``zoneinfo.ZoneInfo`` is the standard library
    solution for timezone handling.
    """

    MESSAGE = (
        "Use `zoneinfo.ZoneInfo` for timezone handling instead of "
        "legacy timezone utilities."
    )

    VALID = [
        Valid("from zoneinfo import ZoneInfo; tz = ZoneInfo('UTC')"),
        Valid("from zoneinfo import ZoneInfo; tz = ZoneInfo('Asia/Tokyo')"),
        Valid("import datetime"),
        Valid("datetime.datetime.now()"),
        Valid("from datetime import datetime"),
    ]
    INVALID = [
        Invalid(
            "import datetime; tz = datetime.timezone.utc",
            expected_message=(
                "Use `zoneinfo.ZoneInfo('UTC')` instead of "
                "`datetime.timezone.utc`."
            ),
        ),
        Invalid(
            "from datetime import timezone; tz = timezone.utc",
            expected_message=(
                "Use `zoneinfo.ZoneInfo('UTC')` instead of "
                "`datetime.timezone.utc`."
            ),
        ),
        Invalid(
            "import pytz",
            expected_message=(
                "Use `zoneinfo.ZoneInfo` instead of `pytz`. "
                "The `pytz` library is no longer necessary "
                "since Python 3.9."
            ),
        ),
        Invalid(
            "from pytz import timezone",
            expected_message=(
                "Use `zoneinfo.ZoneInfo` instead of `pytz`. "
                "The `pytz` library is no longer necessary "
                "since Python 3.9."
            ),
        ),
        Invalid(
            "from dateutil import tz",
            expected_message=(
                "Use `zoneinfo.ZoneInfo` instead of `dateutil.tz`. "
                "The `dateutil.tz` module is no longer necessary "
                "since Python 3.9."
            ),
        ),
        Invalid(
            "from dateutil.tz import gettz",
            expected_message=(
                "Use `zoneinfo.ZoneInfo` instead of `dateutil.tz`. "
                "The `dateutil.tz` module is no longer necessary "
                "since Python 3.9."
            ),
        ),
        Invalid(
            "import dateutil.tz",
            expected_message=(
                "Use `zoneinfo.ZoneInfo` instead of `dateutil.tz`. "
                "The `dateutil.tz` module is no longer necessary "
                "since Python 3.9."
            ),
        ),
    ]

    def visit_Attribute(self, node: cst.Attribute) -> None:
        # datetime.timezone.utc
        if m.matches(
            node,
            m.Attribute(
                value=m.Attribute(
                    value=m.Name("datetime"),
                    attr=m.Name("timezone"),
                ),
                attr=m.Name("utc"),
            ),
        ):
            self.report(
                node,
                "Use `zoneinfo.ZoneInfo('UTC')` instead of "
                "`datetime.timezone.utc`.",
            )
            return

        # timezone.utc (from datetime import timezone)
        if m.matches(
            node,
            m.Attribute(
                value=m.Name("timezone"),
                attr=m.Name("utc"),
            ),
        ):
            self.report(
                node,
                "Use `zoneinfo.ZoneInfo('UTC')` instead of "
                "`datetime.timezone.utc`.",
            )

    def visit_Import(self, node: cst.Import) -> None:
        if isinstance(node.names, cst.ImportStar):
            return

        for alias in node.names:
            name = alias.name

            # import pytz
            if m.matches(name, m.Name("pytz")):
                self.report(
                    node,
                    "Use `zoneinfo.ZoneInfo` instead of `pytz`. "
                    "The `pytz` library is no longer necessary "
                    "since Python 3.9.",
                )

            # import dateutil.tz
            if m.matches(
                name,
                m.Attribute(value=m.Name("dateutil"), attr=m.Name("tz")),
            ):
                self.report(
                    node,
                    "Use `zoneinfo.ZoneInfo` instead of `dateutil.tz`. "
                    "The `dateutil.tz` module is no longer necessary "
                    "since Python 3.9.",
                )

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        if node.module is None:
            return

        # from pytz import ...
        if m.matches(node.module, m.Name("pytz")):
            self.report(
                node,
                "Use `zoneinfo.ZoneInfo` instead of `pytz`. "
                "The `pytz` library is no longer necessary "
                "since Python 3.9.",
            )
            return

        # from dateutil import tz
        if m.matches(node.module, m.Name("dateutil")):
            if isinstance(node.names, cst.ImportStar):
                return
            for alias in node.names:
                if m.matches(alias.name, m.Name("tz")):
                    self.report(
                        node,
                        "Use `zoneinfo.ZoneInfo` instead of "
                        "`dateutil.tz`. "
                        "The `dateutil.tz` module is no longer "
                        "necessary since Python 3.9.",
                    )
                    return

        # from dateutil.tz import ...
        if m.matches(
            node.module,
            m.Attribute(value=m.Name("dateutil"), attr=m.Name("tz")),
        ):
            self.report(
                node,
                "Use `zoneinfo.ZoneInfo` instead of `dateutil.tz`. "
                "The `dateutil.tz` module is no longer necessary "
                "since Python 3.9.",
            )
