import httpx

from easyapi import EasyAPI


def client_for(app):
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


class HeaderMiddleware:
    def __init__(self, app, value="1"):
        self.app = app
        self.value = value

    async def __call__(self, scope, receive, send):
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                message["headers"] = [*message["headers"], (b"x-test", self.value.encode())]
            await send(message)

        await self.app(scope, receive, send_wrapper)


async def test_middleware_adds_header_with_options():
    app = EasyAPI()

    @app.get("/")
    async def index():
        return {}

    app.add_middleware(HeaderMiddleware, value="hello")
    async with client_for(app) as c:
        r = await c.get("/")
    assert r.headers["x-test"] == "hello"


async def test_middleware_wraps_404_too():
    app = EasyAPI()
    app.add_middleware(HeaderMiddleware)
    async with client_for(app) as c:
        r = await c.get("/nope")
    assert r.status_code == 404
    assert r.headers["x-test"] == "1"


async def test_middleware_order_last_added_is_outermost():
    app = EasyAPI()
    calls = []

    def make(name):
        class MW:
            def __init__(self, app):
                self.app = app

            async def __call__(self, scope, receive, send):
                calls.append(f"{name}-in")
                await self.app(scope, receive, send)
                calls.append(f"{name}-out")

        return MW

    app.add_middleware(make("A"))
    app.add_middleware(make("B"))
    async with client_for(app) as c:
        await c.get("/")
    assert calls == ["B-in", "A-in", "A-out", "B-out"]