"""Исключения. Не импортирует ничего из проекта."""

from http import HTTPStatus


class HTTPException(Exception):
    def __init__(
        self,
        status_code: int,
        detail: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status_code = status_code
        self.detail = detail if detail is not None else HTTPStatus(status_code).phrase
        self.headers = headers
        super().__init__(self.detail)


class ParameterError(ValueError):
    """Параметр запроса отсутствует или не приводится к нужному типу."""