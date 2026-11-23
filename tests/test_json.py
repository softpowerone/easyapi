import httpx

from easyapi import EasyAPI, JSONResponse, Response


async def client_for(app):
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


async def test_dict_becomes_json():
    app = EasyAPI()

    @app.get("/user/{id}")
    async def user(id: int):
        return {"id": id, "name": "боб"}

    async with await client_for(app) as c:
        r = await c.get("/user/1")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/json"
    assert r.json() == {"id": 1, "name": "боб"}


async def test_list_becomes_json():
    app = EasyAPI()

    @app.get("/items")
    async def items():
        return [1, 2, 3]

    async with await client_for(app) as c:
        assert (await c.get("/items")).json() == [1, 2, 3]


async def test_response_passes_through():
    app = EasyAPI()

    @app.get("/text")
    async def text():
        return Response("plain")

    async with await client_for(app) as c:
        r = await c.get("/text")
    assert r.text == "plain"
    assert r.headers["content-type"].startswith("text/plain")


async def test_json_response_custom_status():
    app = EasyAPI()

    @app.get("/nope")
    async def nope():
        return JSONResponse({"error": "gone"}, status=410)

    async with await client_for(app) as c:
        r = await c.get("/nope")
    assert r.status_code == 410
    assert r.json() == {"error": "gone"}