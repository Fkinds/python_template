import logging


class LoggerFactoryImpl:
    """getLogger 経由で Logger を生成するファクトリ."""

    def build(self, name: str) -> logging.Logger:
        """指定名の Logger を生成する."""
        return logging.getLogger(name)
