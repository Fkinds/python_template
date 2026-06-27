"""著者の URL ルーティング (composition root)."""

from rest_framework.routers import DefaultRouter

from authors.infrastructure.containers.author import container
from authors.interfaces.views.author import AuthorViewSet
from authors.usecases.protocols import AuthorCrudUseCase

AuthorViewSet.use_case_resolver = lambda: container.injector.get(
    AuthorCrudUseCase,  # type: ignore[type-abstract]
)

router = DefaultRouter()
router.register(r"authors", AuthorViewSet, basename="author")

urlpatterns = router.urls
