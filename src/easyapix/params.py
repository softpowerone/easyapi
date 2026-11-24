"""Сборка аргументов handler по его сигнатуре."""

import inspect
import types
from typing import Any, Union, get_args, get_origin, get_type_hints
from pydantic import BaseModel

from ._types import Handler
from .concurrency import call_maybe_sync
from .dependencies import Depends
from .exeptions import ParameterError
from .requests import Request


def is_model(annotation) -> bool:
    return inspect.isclass(annotation) and issubclass(annotation, BaseModel)

def convert(value: str, annotation: Any) -> Any:
    origin = get_origin(annotation)
    if origin is Union or origin is types.UnionType:
        args = [a for a in get_args(annotation) if a is not type(None)]
        if len(args) == 1:
            annotation = args[0]
    try:
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
    except ValueError as exc:
        raise ParameterError(f"invalid value {value!r}") from exc

async def build_kwargs(handler: Handler, request: Request, path_params: dict[str, str], cache=None) -> dict[str, Any]:
    cache = {} if cache is None else cache
    sig = inspect.signature(handler)
    hints = get_type_hints(handler)
    kwargs: dict[str, Any] = {}
    for name, param in sig.parameters.items():
        if name == "request":
            kwargs[name] = request
        elif isinstance(param.default, Depends):
            dep = param.default.dependency
            if dep not in cache:
                sub_kwargs = await build_kwargs(dep, request, path_params, cache)
                cache[dep] = await call_maybe_sync(dep, **sub_kwargs)
            kwargs[name] = cache[dep]
        elif is_model(hints.get(name)):
            raw = await request.body()
            kwargs[name] = hints[name].model_validate_json(raw)
        elif name in path_params:
            kwargs[name] = convert(path_params[name], hints.get(name, str))
        elif name in request.query_params:
            kwargs[name] = convert(request.query_params[name], hints.get(name, str))

        elif param.default is inspect.Parameter.empty:
            raise ParameterError(f"missing query parameter: {name}")
    return kwargs