from contextlib import asynccontextmanager

from easyapi import EasyAPI


async def run_lifespan(app):
    sent = []
    incoming = [{"type": "lifespan.startup"}, {"type": "lifespan.shutdown"}]

    async def receive():
        return incoming.pop(0)

    async def send(message):
        sent.append(message["type"])

    await app({"type": "lifespan"}, receive, send)
    return sent


async def test_lifespan_without_handler():
    sent = await run_lifespan(EasyAPI())
    assert sent == ["lifespan.startup.complete", "lifespan.shutdown.complete"]


async def test_lifespan_runs_startup_and_shutdown_in_order():
    events = []

    @asynccontextmanager
    async def lifespan(app):
        events.append("start")
        yield
        events.append("stop")

    sent = await run_lifespan(EasyAPI(lifespan=lifespan))
    assert events == ["start", "stop"]
    assert sent == ["lifespan.startup.complete", "lifespan.shutdown.complete"]


async def test_startup_failure():
    @asynccontextmanager
    async def lifespan(app):
        raise RuntimeError("no db")
        yield

    sent = []
    incoming = [{"type": "lifespan.startup"}]

    async def receive():
        return incoming.pop(0)

    async def send(message):
        sent.append(message)

    await EasyAPI(lifespan=lifespan)({"type": "lifespan"}, receive, send)
    assert sent == [{"type": "lifespan.startup.failed", "message": "no db"}]


async def test_shutdown_failure():
    @asynccontextmanager
    async def lifespan(app):
        yield
        raise RuntimeError("cleanup failed")

    sent = await run_lifespan(EasyAPI(lifespan=lifespan))
    assert sent == ["lifespan.startup.complete", "lifespan.shutdown.failed"]