"""ファクトリ層の例外クラス."""


class FactoryError(Exception):
    """ファクトリに関連するエラーの基底クラス."""

    pass


class GenerateFactoryError(FactoryError):
    """ファクトリの生成に失敗した場合に発生する例外."""

    pass
