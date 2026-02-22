import logging
from typing import Any

from rest_framework import viewsets
from rest_framework.parsers import FormParser
from rest_framework.parsers import JSONParser
from rest_framework.parsers import MultiPartParser
from rest_framework.serializers import BaseSerializer

from books.entities import Book
from books.serializers import BookDetailSerializer
from books.serializers import BookSerializer
from notifications.domain.events import BookCreated
from notifications.domain.results import NotificationProblem
from notifications.infrastructure.containers.notificaton import (
    get_book_created_use_case,
)

logger = logging.getLogger(__name__)


class BookViewSet(viewsets.ModelViewSet[Book]):
    queryset = Book.objects.select_related("author").all()
    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser,
    ]

    def get_serializer_class(
        self,
    ) -> type[BookSerializer | BookDetailSerializer]:
        if self.action in ("list", "retrieve"):
            return BookDetailSerializer
        return BookSerializer

    def perform_create(self, serializer: BaseSerializer[Any]) -> None:
        """本の作成時に通知を送信する."""
        instance = serializer.save()
        event = BookCreated(
            title=instance.title,
            isbn=instance.isbn,
            author_name=instance.author.name,
        )
        result = get_book_created_use_case().execute(
            event=event,
        )
        if isinstance(result, NotificationProblem):
            logger.warning(
                "通知送信に失敗しました: %s",
                result.detail,
            )
