from rest_framework import viewsets

from books.models import Author
from books.models import Book
from books.serializers import AuthorSerializer
from books.serializers import BookDetailSerializer
from books.serializers import BookSerializer


class AuthorViewSet(viewsets.ModelViewSet[Author]):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class BookViewSet(viewsets.ModelViewSet[Book]):
    queryset = Book.objects.select_related("author").all()

    def get_serializer_class(
        self,
    ) -> type[BookSerializer | BookDetailSerializer]:
        if self.action in ("list", "retrieve"):
            return BookDetailSerializer
        return BookSerializer
