from pathlib import Path

import pytest
from fixit.engine import LintRunner
from fixit.ftypes import Config

from lint_rules.use_zoneinfo import UseZoneInfo


@pytest.fixture
def config() -> Config:
    return Config(path=Path("test.py"))


def _lint(
    source: str,
    config: Config,
) -> list[str]:
    runner = LintRunner(config.path, source.encode())
    rule = UseZoneInfo()
    reports = list(runner.collect_violations([rule], config))
    return [r.message for r in reports]


class TestUseZoneInfoValid:
    """ルールが誤検出しないケース"""

    def test_zoneinfo_utc_is_allowed(self, config: Config) -> None:
        code = "from zoneinfo import ZoneInfo; tz = ZoneInfo('UTC')\n"
        assert _lint(code, config) == []

    def test_zoneinfo_named_tz_is_allowed(self, config: Config) -> None:
        code = "from zoneinfo import ZoneInfo\ntz = ZoneInfo('Asia/Tokyo')\n"
        assert _lint(code, config) == []

    def test_import_datetime_is_allowed(self, config: Config) -> None:
        assert _lint("import datetime\n", config) == []

    def test_datetime_now_is_allowed(self, config: Config) -> None:
        assert _lint("datetime.datetime.now()\n", config) == []

    def test_from_datetime_import_is_allowed(self, config: Config) -> None:
        assert _lint("from datetime import datetime\n", config) == []

    def test_datetime_timedelta_allowed(self, config: Config) -> None:
        assert _lint("from datetime import timedelta\n", config) == []

    def test_dateutil_parser_allowed(self, config: Config) -> None:
        assert _lint("from dateutil import parser\n", config) == []

    def test_import_dateutil_is_allowed(self, config: Config) -> None:
        assert _lint("import dateutil\n", config) == []

    def test_timezone_string_variable_is_allowed(self, config: Config) -> None:
        assert _lint('timezone = "Asia/Tokyo"\n', config) == []


class TestUseZoneInfoDatetimeTimezoneUtc:
    """datetime.timezone.utc の検出"""

    def test_datetime_timezone_utc(self, config: Config) -> None:
        code = "import datetime; tz = datetime.timezone.utc\n"
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "ZoneInfo('UTC')" in messages[0]

    def test_timezone_utc_from_import(self, config: Config) -> None:
        code = "from datetime import timezone\ntz = timezone.utc\n"
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "ZoneInfo('UTC')" in messages[0]

    def test_datetime_timezone_utc_as_argument(self, config: Config) -> None:
        code = "datetime.datetime.now(datetime.timezone.utc)\n"
        messages = _lint(code, config)
        assert len(messages) == 1
        assert "ZoneInfo('UTC')" in messages[0]


class TestUseZoneInfoPytz:
    """pytz の検出"""

    def test_import_pytz(self, config: Config) -> None:
        messages = _lint("import pytz\n", config)
        assert len(messages) == 1
        assert "pytz" in messages[0]

    def test_from_pytz_import_timezone(self, config: Config) -> None:
        messages = _lint("from pytz import timezone\n", config)
        assert len(messages) == 1
        assert "pytz" in messages[0]

    def test_from_pytz_import_utc(self, config: Config) -> None:
        messages = _lint("from pytz import UTC\n", config)
        assert len(messages) == 1
        assert "pytz" in messages[0]

    def test_import_pytz_with_alias(self, config: Config) -> None:
        messages = _lint("import pytz as tz\n", config)
        assert len(messages) == 1
        assert "pytz" in messages[0]


class TestUseZoneInfoDateutil:
    """dateutil.tz の検出"""

    def test_from_dateutil_import_tz(self, config: Config) -> None:
        messages = _lint("from dateutil import tz\n", config)
        assert len(messages) == 1
        assert "dateutil.tz" in messages[0]

    def test_from_dateutil_tz_import(self, config: Config) -> None:
        messages = _lint("from dateutil.tz import gettz\n", config)
        assert len(messages) == 1
        assert "dateutil.tz" in messages[0]

    def test_import_dateutil_tz(self, config: Config) -> None:
        messages = _lint("import dateutil.tz\n", config)
        assert len(messages) == 1
        assert "dateutil.tz" in messages[0]

    def test_from_dateutil_import_tz_with_others(self, config: Config) -> None:
        messages = _lint("from dateutil import tz, parser\n", config)
        assert len(messages) == 1
        assert "dateutil.tz" in messages[0]
