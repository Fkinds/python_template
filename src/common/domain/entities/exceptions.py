"""共通ドメイン例外クラス."""


class EntityError(Exception):
    """エンティティに関連するエラーの基底クラス."""

    pass


class EntityDoesNotExistError(EntityError):
    """エンティティが見つからない場合に発生する例外."""

    pass


class GenerateRepositoryError(EntityError):
    """リポジトリの生成に失敗した場合に発生する例外."""

    pass
