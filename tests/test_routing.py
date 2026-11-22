import httpx

from easyapi import EasyAPI, Response
from easyapi.routing import Router


def test_resolve_found():
    router = Router()

    async def h(request): ...

    router.add_route("GET", "/a", h)
    assert router.resolve("GET", "/a") == (h, ["GET"])


def test_resolve_404():
    assert Router().resolve("GET", "/nope") == (None, [])


def test_resolve_405():
    router = Router()

    async def h(request): ...

    router.add_route("GET", "/a", h)
    assert router.resolve("POST", "/a") == (None, ["GET"])


async def client_for(app):
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


async def test_app_routes():
    app = EasyAPI()

    @app.get("/ping")
    async def ping(request):
        return Response("pong")

    async with await client_for(app) as c:
        assert (await c.get("/ping")).text == "pong"
        assert (await c.get("/nope")).status_code == 404
        r = await c.post("/ping")
        assert r.status_code == 405
        assert r.headers["allow"] == "GET"