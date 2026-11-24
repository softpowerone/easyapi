"""класс EasyAPI"""
import json
import logging

from pydantic import ValidationError

from ._types import Scope, Receive, Send
from .concurrency import call_maybe_sync
from .exeptions import HTTPException
from .params import build_kwargs
from .requests import Request
from .responses import Response, make_response, JSONResponse
from .routing import Router

logger = logging.getLogger("easyapi")


class EasyAPI:
    def __init__(self) -> None:
        self.router = Router()
        self._stack = self._dispatch

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

    def add_middleware(self, middleware_class, **options) -> None:
        self._stack = middleware_class(self._stack, **options)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self._stack(scope, receive, send)

    async def _dispatch(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return
        request = Request(scope, receive)
        response = await self._handle(request)
        await response(send)

    async def _handle(self, request: Request) -> Response:
        handler, allowed, path_params = self.router.resolve(request.method, request.path)

        if handler is None:
            if allowed:
                return JSONResponse(
                    {"detail": "Method Not Allowed"},
                    status=405,
                    headers={"allow": ", ".join(sorted(allowed))},
                )
            return JSONResponse({"detail": "Not Found"}, status=404)

        try:
            try:
                kwargs = await build_kwargs(handler, request, path_params)
            except ValidationError as exc:
                return JSONResponse(
                    {"detail": json.loads(exc.json(include_url=False))}, status=422
                )
            except ValueError as exc:
                return JSONResponse({"detail": str(exc)}, status=422)
            return make_response(await call_maybe_sync(handler, **kwargs))
        except HTTPException as exc:
            return JSONResponse({"detail": exc.detail}, status=exc.status_code, headers=exc.headers)
        except Exception:
            logger.exception("Unhandled error in %s %s", request.method, request.path)
            return JSONResponse({"detail": "Internal Server Error"}, status=500)
