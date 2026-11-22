"""Выбор handler по методу и пути."""

from collections.abc import Callable

from easyapi._types import Handler


class Router:
    def __init__(self) -> None:
        # {"/hello": {"GET": handler, "POST": handler}}
        self._routes: dict[str, dict[str, Handler]] = {}

    def add_route(self, method: str, path: str, handler: Handler) -> None:
        self._routes.setdefault(path, {})[method.upper()] = handler

    def get(self, path: str) -> Callable[[Handler], Handler]:
        def decorator(handler: Handler) -> Handler:
            self.add_route("GET", path, handler)
            return handler
        return decorator

    def resolve(self, method: str, path: str) -> tuple[Handler | None, list[str]]:
        methods = self._routes.get(path, {})
        allowed = list(methods)
        handler = methods.get(method.upper())
        return handler, allowed