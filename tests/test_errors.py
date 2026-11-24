import httpx

from easyapix import Depends, EasyAPIx, HTTPException


def client_for(app):
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


async def test_404_is_json():
    async with client_for(EasyAPIx()) as c:
        r = await c.get("/nope")
    assert r.status_code == 404
    assert r.json() == {"detail": "Not Found"}


async def test_405_is_json_with_allow():
    app = EasyAPIx()

    @app.get("/a")
    async def a():
        return {}

    async with client_for(app) as c:
        r = await c.post("/a")
    assert r.status_code == 405
    assert r.json() == {"detail": "Method Not Allowed"}
    assert r.headers["allow"] == "GET"


async def test_http_exception_in_handler():
    app = EasyAPIx()

    @app.get("/u/{id}")
    async def u(id: int):
        raise HTTPException(404, "no such user")

    async with client_for(app) as c:
        r = await c.get("/u/1")
    assert r.status_code == 404
    assert r.json() == {"detail": "no such user"}


async def test_http_exception_default_detail_and_headers():
    app = EasyAPIx()

    @app.get("/x")
    async def x():
        raise HTTPException(401, headers={"www-authenticate": "Bearer"})

    async with client_for(app) as c:
        r = await c.get("/x")
    assert r.json() == {"detail": "Unauthorized"}
    assert r.headers["www-authenticate"] == "Bearer"


async def test_http_exception_in_dependency():
    app = EasyAPIx()

    def guard():
        raise HTTPException(401, "nope")

    @app.get("/x")
    async def x(g=Depends(guard)):
        return {}

    async with client_for(app) as c:
        assert (await c.get("/x")).status_code == 401


async def test_unexpected_error_is_500():
    app = EasyAPIx()

    @app.get("/boom")
    async def boom():
        raise RuntimeError("secret internals")

    async with client_for(app) as c:
        r = await c.get("/boom")
    assert r.status_code == 500
    assert r.json() == {"detail": "Internal Server Error"}


async def test_value_error_in_handler_is_500_not_422():
    app = EasyAPIx()

    @app.get("/x")
    async def x():
        raise ValueError("bug in my code")

    async with client_for(app) as c:
        assert (await c.get("/x")).status_code == 500


async def test_value_error_in_dependency_is_500():
    app = EasyAPIx()

    def dep():
        raise ValueError("bug")

    @app.get("/x")
    async def x(d=Depends(dep)):
        return {}

    async with client_for(app) as c:
        assert (await c.get("/x")).status_code == 500