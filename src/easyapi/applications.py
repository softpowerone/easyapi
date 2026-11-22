"""класс EasyAPI"""
from easyapi.requests import Request
from easyapi.responses import Response


class EasyAPI:
    ...

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return

        request = Request(scope, receive)
        name = request.query_params.get("name", "world")
        response = Response(f"Hello, {name}")
        await response(send)