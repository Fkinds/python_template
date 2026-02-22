from rest_framework import viewsets
from rest_framework.parsers import FormParser
from rest_framework.parsers import JSONParser
from rest_framework.parsers import MultiPartParser

from books.entities import Book
from books.serializers import BookDetailSerializer
from books.serializers import BookSerializer


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
