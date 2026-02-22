from django.core.validators import MinLengthValidator
from django.db import models

from books.entities.safe_text import SafeText

TITLE_MIN_LENGTH = 1
TITLE_MAX_LENGTH = 255
ISBN_LENGTH = 13


class Book(models.Model):
    title = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        validators=[MinLengthValidator(TITLE_MIN_LENGTH)],
    )
    isbn = models.CharField(max_length=ISBN_LENGTH, unique=True)
    published_date = models.DateField()
    author = models.ForeignKey(
        "authors.Author",
        on_delete=models.CASCADE,
        related_name="books",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_date"]

    def __str__(self) -> str:
        return self.title

    @property
    def title_vo(self) -> SafeText:
        return SafeText(
            value=self.title,
            min_length=TITLE_MIN_LENGTH,
            max_length=TITLE_MAX_LENGTH,
        )
