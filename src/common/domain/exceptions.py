"""アプリケーション例外の頂点クラス.

全例外はこの ``AppError`` を頂点とするピラミッドに属する。
頂点を一本化することで、未捕捉でのリーク (取りこぼし) と
握り潰しを構造的に検出・防止しやすくする。

ドメイン層に置くことで、外側の全レイヤから参照できる
(依存方向: domain <- usecases <- interfaces <- infrastructure)。
stdlib のみに依存する。
"""


class AppError(Exception):
    """アプリケーション全例外の基底 (ピラミッドの頂点)."""

    pass
