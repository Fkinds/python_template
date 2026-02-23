import logging
from typing import Protocol
from typing import runtime_checkable


@runtime_checkable
class LoggerFactory(Protocol):
    """Logger 生成のポート."""

    def build(self, name: str) -> logging.Logger: ...
