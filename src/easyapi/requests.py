"""Удобный доступ к данным входящего HTTP-запроса."""

from urllib.parse import parse_qsl


class Request:
    def __init__(self, scope, receive):
        self._scope = scope
        self._receive = receive
        self._body: bytes | None = None

    @property
    def method(self) -> str:
        return self._scope["method"]

    @property
    def path(self) -> str:
        return self._scope["path"]

    @property
    def query_params(self) -> dict[str, str]:
        raw = self._scope["query_string"].decode()
        return dict(parse_qsl(raw))

    @property
    def headers(self) -> dict[str, str]:
        return {
            key.decode().lower(): value.decode()
            for key, value in self._scope["headers"]
        }

    async def body(self) -> bytes:
        if self._body is None:
            chunks = b""
            while True:
                message = await self._receive()
                chunks += message.get("body", b"")
                if not message.get("more_body", False):
                    break
            self._body = chunks
        return self._body