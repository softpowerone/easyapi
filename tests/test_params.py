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