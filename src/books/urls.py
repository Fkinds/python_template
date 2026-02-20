from rest_framework.routers import DefaultRouter

from books.views import AuthorViewSet
from books.views import BookViewSet

router = DefaultRouter()
router.register(r"authors", AuthorViewSet)
router.register(r"books", BookViewSet)

urlpatterns = router.urls
