from injector import Injector
from injector import Module


class ContainerHolder:
    """DI コンテナの保持と差し替えを管理する."""

    def __init__(self, *modules: Module) -> None:
        self._default_modules = modules
        self._injector = Injector(list(modules))

    @property
    def injector(self) -> Injector:
        return self._injector

    def override(self, *modules: Module) -> None:
        self._injector = Injector(list(modules))

    def reset(self) -> None:
        self._injector = Injector(
            list(self._default_modules),
        )
