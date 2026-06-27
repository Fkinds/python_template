"""著者の出力シリアライザ."""

from typing import Any

from rest_framework import serializers


class AuthorSerializer(serializers.Serializer[Any]):
    """著者シリアライザ (read-only)."""

    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    bio = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
