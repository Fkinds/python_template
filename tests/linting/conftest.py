"""lint ルールテスト用フィクスチャ.

fixit LintRunner に渡す共通 Config を提供する.
"""

from pathlib import Path

import pytest
from fixit.ftypes import Config


@pytest.fixture
def config() -> Config:
    """lint テスト用の最小 Config."""
    return Config(path=Path("test.py"))
