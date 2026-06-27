"""リポジトリ層の例外クラス."""

from common.domain.exceptions import AppError


class RepositoryError(AppError):
    """リポジトリに関連するエラーの基底クラス."""

    pass
