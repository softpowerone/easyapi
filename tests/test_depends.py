import httpx

from easyapi import Depends, EasyAPI


def client_for(app):
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


async def test_simple_dependency():
    app = EasyAPI()

    def get_value():
        return 42

    @app.get("/x")
    async def x(v: int = Depends(get_value)):
        return {"v": v}

    async with client_for(app) as c:
        assert (await c.get("/x")).json() == {"v": 42}


async def test_async_dependency():
    app = EasyAPI()

    async def get_value():
        return "async"

    @app.get("/x")
    async def x(v: str = Depends(get_value)):
        return {"v": v}

    async with client_for(app) as c:
        assert (await c.get("/x")).json() == {"v": "async"}


async def test_nested_dependency():
    app = EasyAPI()

    def base():
        return 10

    def doubled(b: int = Depends(base)):
        return b * 2

    @app.get("/x")
    async def x(d: int = Depends(doubled)):
        return {"d": d}

    async with client_for(app) as c:
        assert (await c.get("/x")).json() == {"d": 20}


async def test_dependency_uses_query_param():
    app = EasyAPI()

    def get_user(user: str = "anon"):
        return user

    @app.get("/me")
    async def me(u: str = Depends(get_user)):
        return {"user": u}

    async with client_for(app) as c:
        assert (await c.get("/me")).json() == {"user": "anon"}
        assert (await c.get("/me", params={"user": "bob"})).json() == {"user": "bob"}


async def test_dependency_called_once_per_request():
    app = EasyAPI()
    calls = []

    def counter():
        calls.append(1)
        return len(calls)

    def a(c: int = Depends(counter)):
        return c

    @app.get("/x")
    async def x(first: int = Depends(counter), second: int = Depends(a)):
        return {"first": first, "second": second}

    async with client_for(app) as c:
        r = await c.get("/x")
    assert r.json() == {"first": 1, "second": 1}
    assert len(calls) == 1


async def test_dependency_missing_required_param_422():
    app = EasyAPI()

    def need_token(token: str):
        return token

    @app.get("/x")
    async def x(t: str = Depends(need_token)):
        return {"t": t}

    async with client_for(app) as c:
        assert (await c.get("/x")).status_code == 422