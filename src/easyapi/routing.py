"""Выбор handler по методу и пути."""

import re
from collections.abc import Callable
from dataclasses import dataclass, field

from ._types import Handler

_PARAM_RE = re.compile(r"{(\w+)}")


def compile_path(path: str) -> re.Pattern[str]:
    """'/hello/{name}' -> ^/hello/(?P<name>[^/]+)$"""
    regex, pos = "", 0
    for m in _PARAM_RE.finditer(path):
        regex += re.escape(path[pos:m.start()]) + f"(?P<{m.group(1)}>[^/]+)"
        pos = m.end()
    regex += re.escape(path[pos:])
    return re.compile(f"^{regex}$")


@dataclass
class Route:
    path: str
    pattern: re.Pattern[str]
    methods: dict[str, Handler] = field(default_factory=dict)


class Router:
    def __init__(self) -> None:
        # {"/hello": {"GET": handler, "POST": handler}}
        self._routes: list[Route] = []

    def add_route(self, method: str, path: str, handler: Handler) -> None:
        for route in self._routes:
            if route.path == path:
                route.methods[method.upper()] = handler
                return
        route = Route(path, compile_path(path))
        route.methods[method.upper()] = handler
        self._routes.append(route)

    def get(self, path: str) -> Callable[[Handler], Handler]:
        def decorator(handler: Handler) -> Handler:
            self.add_route("GET", path, handler)
            return handler
        return decorator

    def resolve(self, method: str, path: str) -> tuple[Handler | None, list[str], dict[str, str]]:
        for route in self._routes:
            match = route.pattern.match(path)
            if match:
                params = match.groupdict()
                allowed = list(route.methods)
                handler = route.methods.get(method.upper())
                return handler, allowed, params
        return None, [], {}