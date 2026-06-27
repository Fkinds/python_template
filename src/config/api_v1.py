"""api/v1 のルーティング集約.

各コンテキストが公開する urlconf を v1 名前空間の下に束ねる
合成点 (Composition Root)。バージョンの増設はこのファイルを
複製する形で行う。

NOTE: 現状 reverse() は不使用のため app_name/namespace を付けていない。
v2 を追加し URL 名が衝突し得る段階で namespace を付与すること。
"""

from django.urls import include
from django.urls import path

urlpatterns = [
    path("", include("authors.urls")),
    path("", include("books.urls")),
    path("", include("notifications.infrastructure.routing.urls")),
]
