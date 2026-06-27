"""著者の DI バインディング."""

from typing import Any

import injector

from authors.interfaces.repositories.author import AuthorRepositoryImpl
from authors.usecases.crud import AuthorCrudUseCaseImpl
from authors.usecases.protocols import AuthorCrudUseCase
from authors.usecases.protocols import AuthorRepository
from common.infrastructure.containers.di import ContainerHolder


class AuthorModule(injector.Module):
    """著者の DI を構成するモジュール.

    テストでは repository_override に Fake を渡して差し替える。
    """

    # lint-fixme: ParamLineBreak: 79文字制限で改行が必要
    def __init__(
        self,
        repository_override: AuthorRepository | None = None,
    ) -> None:
        self._repository: Any = repository_override or AuthorRepositoryImpl()

    def configure(self, binder: injector.Binder) -> None:
        binder.bind(
            AuthorRepository,  # type: ignore[type-abstract]
            to=self._repository,
        )
        binder.bind(
            AuthorCrudUseCase,  # type: ignore[type-abstract]
            to=AuthorCrudUseCaseImpl,
        )


container = ContainerHolder(AuthorModule())
