from rest_framework.routers import DefaultRouter

from authors.views import AuthorViewSet

router = DefaultRouter()
router.register(r"authors", AuthorViewSet)

urlpatterns = router.urls
