"""класс EasyAPI"""
import json

from pydantic import ValidationError

from .params import build_kwargs
from .requests import Request
from .responses import Response, make_response, JSONResponse
from .routing import Router


class EasyAPI:
    def __init__(self) -> None:
        self.router = Router()

    def get(self, path: str):
        return self.router.get(path)

    def post(self, path: str):
        return self.router.post(path)

    def put(self, path: str):
        return self.router.put(path)

    def patch(self, path: str):
        return self.router.patch(path)

    def delete(self, path: str):
        return self.router.delete(path)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return

        request = Request(scope, receive)
        handler, allowed, path_params = self.router.resolve(request.method, request.path)

        if handler is not None:
            try:
                kwargs = await build_kwargs(handler, request, path_params)
            except ValidationError as exc:
                response = JSONResponse(
                    {"detail": json.loads(exc.json(include_url=False))}, status=422
                )
            except ValueError as exc:
                response = JSONResponse({"detail": str(exc)}, status=422)
            else:
                response = make_response(await handler(**kwargs))

        elif allowed:
            response = Response(
                "Method Not Allowed",
                status=405,
                headers={"allow": ", ".join(sorted(allowed))},
            )
        else:
            response = Response("Not Found", status=404)

        await response(send)