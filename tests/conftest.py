"""テストスイート共通設定.

フィクスチャは各テストサイズディレクトリの conftest.py に配置する.
pytest マーカーはディレクトリ名から自動付与する.
"""

from pathlib import Path

import pytest

_SIZE_DIRS: frozenset[str] = frozenset(
    {"unit", "integration", "functional", "linting"}
)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """テストファイルのパスからサイズマーカーを自動付与する."""
    for item in items:
        path = Path(item.fspath)
        for parent in path.parents:
            if parent.name in _SIZE_DIRS:
                item.add_marker(getattr(pytest.mark, parent.name))
                break
