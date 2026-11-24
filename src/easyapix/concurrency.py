"""Вызов sync- и async-функций единым способом."""

import asyncio
import functools
import inspect
from collections.abc import Callable
from typing import Any


async def call_maybe_sync(func: Callable[..., Any], **kwargs: Any) -> Any:
    if inspect.iscoroutinefunction(func):
        return await func(**kwargs)
    result = await asyncio.to_thread(functools.partial(func, **kwargs))
    if inspect.isawaitable(result):
        result = await result
    return result
