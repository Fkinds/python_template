"""著者の入力デシリアライザ (検証).

入力の構文・形式エラーはここで検出し、DRF の ValidationError として
400 を返す (ドメイン不変条件違反の 422 とは別概念)。
"""

from typing import Any

from rest_framework import serializers


class AuthorDeserializer(serializers.Serializer[Any]):
    """著者の作成/更新入力を検証する."""

    name = serializers.CharField(max_length=255)
    bio = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )
