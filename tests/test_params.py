import httpx
import pytest

from easyapi import EasyAPI, Response
from easyapi.params import convert


def test_convert():
    assert convert("5", int) == 5
    assert convert("1.5", float) == 1.5
    assert convert("x", str) == "x"
    assert convert("true", bool) is True
    with pytest.raises(ValueError):
        convert("abc", int)


async def test_path_params_end_to_end():
    app = EasyAPI()

    @app.get("/square/{n}")
    async def square(n: int):
        return Response(str(n * n))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        assert (await c.get("/square/5")).text == "25"
        assert (await c.get("/square/abc")).status_code == 422

async def make_client():
    app = EasyAPI()

    @app.get("/greet")
    async def greet(name: str = "world"):
        return Response(f"Hello, {name}")

    @app.get("/add")
    async def add(a: int, b: int = 0):
        return Response(str(a + b))

    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


async def test_query_default():
    async with await make_client() as c:
        assert (await c.get("/greet")).text == "Hello, world"


async def test_query_value():
    async with await make_client() as c:
        assert (await c.get("/greet", params={"name": "bob"})).text == "Hello, bob"


async def test_query_int_and_default():
    async with await make_client() as c:
        assert (await c.get("/add", params={"a": 2, "b": 3})).text == "5"
        assert (await c.get("/add", params={"a": 2})).text == "2"


async def test_query_missing_required_422():
    async with await make_client() as c:
        assert (await c.get("/add")).status_code == 422


async def test_query_bad_type_422():
    async with await make_client() as c:
        assert (await c.get("/add", params={"a": "x"})).status_code == 422