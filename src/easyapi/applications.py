"""класс EasyAPI"""
from .params import build_kwargs
from .requests import Request
from .responses import Response
from .routing import Router


class EasyAPI:
    def __init__(self) -> None:
        self.router = Router()

    def get(self, path: str):
        return self.router.get(path)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return

        request = Request(scope, receive)
        handler, allowed, path_params = self.router.resolve(request.method, request.path)

        if handler is not None:
            try:
                kwargs = build_kwargs(handler, request, path_params)
            except ValueError:
                response = Response("Unprocessable Entity", status=422)
            else:
                response = await handler(**kwargs)

        elif allowed:
            response = Response(
                "Method Not Allowed",
                status=405,
                headers={"allow": ", ".join(sorted(allowed))},
            )
        else:
            response = Response("Not Found", status=404)

        await response(send)