import logging
from typing import Any

from rest_framework import viewsets
from rest_framework.serializers import BaseSerializer

from authors.models import Author
from authors.serializers import AuthorSerializer
from notifications.domain.events import AuthorCreated
from notifications.infrastructure.containers.notificaton import (
    get_author_created_use_case,
)

logger = logging.getLogger(__name__)


class AuthorViewSet(viewsets.ModelViewSet[Author]):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def perform_create(self, serializer: BaseSerializer[Any]) -> None:
        """著者の作成時に通知を送信する."""
        instance = serializer.save()
        event = AuthorCreated(name=instance.name)
        try:
            use_case = get_author_created_use_case()
            use_case.execute(event=event)
        except Exception:
            logger.exception("通知送信に失敗しました")
