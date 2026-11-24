import httpx
from pydantic import BaseModel

from easyapix import EasyAPIx


class Item(BaseModel):
    name: str
    price: float


def make_client():
    app = EasyAPIx()

    @app.post("/items")
    async def create(item: Item):
        return {"name": item.name, "price": item.price}

    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


async def test_valid_body():
    async with make_client() as c:
        r = await c.post("/items", json={"name": "pen", "price": 1.5})
    assert r.status_code == 200
    assert r.json() == {"name": "pen", "price": 1.5}


async def test_invalid_field_422():
    async with make_client() as c:
        r = await c.post("/items", json={"name": "pen", "price": "abc"})
    assert r.status_code == 422
    assert r.json()["detail"][0]["loc"] == ["price"]


async def test_missing_field_422():
    async with make_client() as c:
        assert (await c.post("/items", json={"name": "pen"})).status_code == 422


async def test_broken_json_422():
    async with make_client() as c:
        r = await c.post("/items", content=b"{not json")
    assert r.status_code == 422


async def test_empty_body_422():
    async with make_client() as c:
        assert (await c.post("/items")).status_code == 422