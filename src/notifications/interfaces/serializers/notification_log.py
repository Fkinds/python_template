"""通知履歴のシリアライザ."""

from typing import Any

from rest_framework import serializers


class NotificationLogSerializer(serializers.Serializer[Any]):
    """通知履歴シリアライザ (read-only)."""

    id = serializers.UUIDField(read_only=True)
    event_type = serializers.CharField(
        read_only=True,
    )
    message = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    detail = serializers.CharField(read_only=True)
    recipient = serializers.CharField(read_only=True)
    channel = serializers.CharField(read_only=True)
    retry_count = serializers.IntegerField(
        read_only=True,
    )
    created_at = serializers.DateTimeField(
        read_only=True,
    )
