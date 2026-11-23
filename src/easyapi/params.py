"""Сборка аргументов handler по его сигнатуре."""

import inspect
from typing import Any, get_type_hints

from ._types import Handler
from .requests import Request


def convert(value: str, annotation: Any) -> Any:
    if annotation is int:
        return int(value)
    if annotation is float:
        return float(value)
    if annotation is bool:
        lowered = value.lower()
        if lowered in ("true", "1"):
            return True
        if lowered in ("false", "0"):
            return False
        raise ValueError(f"invalid bool: {value!r}")
    return value


def build_kwargs(handler: Handler, request: Request, path_params: dict[str, str]) -> dict[str, Any]:
    sig = inspect.signature(handler)
    hints = get_type_hints(handler)
    kwargs: dict[str, Any] = {}
    for name, param in sig.parameters.items():
        if name == "request":
            kwargs[name] = request
        elif name in path_params:
            kwargs[name] = convert(path_params[name], hints.get(name, str))
        elif name in request.query_params:
            kwargs[name] = convert(request.query_params[name], hints.get(name, str))

        elif param.default is inspect.Parameter.empty:
            raise ValueError(f"missing query parameter: {name}")
    return kwargs