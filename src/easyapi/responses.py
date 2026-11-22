"""Формирование и отправка HTTP-ответа."""

from ._types import Send


class Response:
    def __init__(
        self,
        body: bytes | str = b"",
        status: int = 200,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status = status
        self.body = body.encode() if isinstance(body, str) else body
        self.headers = {"content-type": "text/plain; charset=utf-8"}
        if headers:
            self.headers.update({k.lower(): v for k, v in headers.items()})

    def _raw_headers(self) -> list[tuple[bytes, bytes]]:
        return [(k.encode(), v.encode()) for k, v in self.headers.items()]

    async def __call__(self, send: Send) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": self.status,
                "headers": self._raw_headers(),
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": self.body,
            }
        )