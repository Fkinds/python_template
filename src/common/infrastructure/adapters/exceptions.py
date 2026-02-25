"""アダプタ層の例外クラス."""


class AdapterError(Exception):
    """アダプタに関連するエラーの基底クラス."""

    pass


class GenerateAdapterError(AdapterError):
    """アダプタの生成に失敗した場合に発生する例外."""

    pass
