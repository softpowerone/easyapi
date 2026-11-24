"""Маркер зависимости. Не импортирует ничего из проекта."""

from collections.abc import Callable
from typing import Any


class Depends:
    def __init__(self, dependency: Callable[..., Any]) -> None:
        self.dependency = dependency