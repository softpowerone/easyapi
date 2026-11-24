import asyncio
import threading
import time

import httpx

from easyapix import Depends, EasyAPIx, HTTPException


def client_for(app):
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


async def test_sync_handler():
    app = EasyAPIx()

    @app.get("/x")
    def x():
        return {"ok": True}

    async with client_for(app) as c:
        assert (await c.get("/x")).json() == {"ok": True}


async def test_sync_handler_with_params():
    app = EasyAPIx()

    @app.get("/sq/{n}")
    def sq(n: int, add: int = 0):
        return {"r": n * n + add}

    async with client_for(app) as c:
        assert (await c.get("/sq/3", params={"add": 1})).json() == {"r": 10}


async def test_sync_handler_runs_in_other_thread():
    app = EasyAPIx()
    main_thread = threading.get_ident()

    @app.get("/t")
    def t():
        return {"same": threading.get_ident() == main_thread}

    async with client_for(app) as c:
        assert (await c.get("/t")).json() == {"same": False}


async def test_sync_dependency():
    app = EasyAPIx()

    def get_value():
        return 7

    @app.get("/x")
    def x(v: int = Depends(get_value)):
        return {"v": v}

    async with client_for(app) as c:
        assert (await c.get("/x")).json() == {"v": 7}


async def test_http_exception_from_sync_handler():
    app = EasyAPIx()

    @app.get("/x")
    def x():
        raise HTTPException(404, "missing")

    async with client_for(app) as c:
        r = await c.get("/x")
    assert r.status_code == 404
    assert r.json() == {"detail": "missing"}


async def test_unexpected_error_in_sync_handler_is_500():
    app = EasyAPIx()

    @app.get("/x")
    def x():
        raise RuntimeError("boom")

    async with client_for(app) as c:
        assert (await c.get("/x")).status_code == 500


async def test_blocking_sync_handler_does_not_block_loop():
    app = EasyAPIx()

    @app.get("/slow")
    def slow():
        time.sleep(0.3)
        return {}

    async with client_for(app) as c:
        start = time.perf_counter()
        await asyncio.gather(c.get("/slow"), c.get("/slow"), c.get("/slow"))
        elapsed = time.perf_counter() - start
    # последовательно было бы ~0.9 с, параллельно ~0.3 с
    assert elapsed < 0.7