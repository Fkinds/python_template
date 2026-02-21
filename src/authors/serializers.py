from rest_framework import serializers

from authors.models import Author


class AuthorSerializer(serializers.ModelSerializer[Author]):
    class Meta:
        model = Author
        fields = ["id", "name", "bio", "created_at"]
        read_only_fields = ["id", "created_at"]
