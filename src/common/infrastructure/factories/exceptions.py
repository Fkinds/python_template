"""ファクトリ層の例外クラス."""

from common.domain.exceptions import AppError


class FactoryError(AppError):
    """ファクトリに関連するエラーの基底クラス."""

    pass


class GenerateFactoryError(FactoryError):
    """ファクトリの生成に失敗した場合に発生する例外."""

    pass
