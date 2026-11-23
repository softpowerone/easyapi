from easyapi.routing import Router


def test_resolve_found():
    router = Router()

    async def h(request): ...

    router.add_route("GET", "/a", h)
    assert router.resolve("GET", "/a") == (h, ["GET"], {})


def test_resolve_404():
    assert Router().resolve("GET", "/nope") == (None, [], {})


def test_resolve_405():
    router = Router()

    async def h(request): ...

    router.add_route("GET", "/a", h)
    assert router.resolve("POST", "/a") == (None, ["GET"], {})


def test_resolve_path_params():
    router = Router()

    async def h(name): ...

    router.add_route("GET", "/hello/{name}", h)
    handler, allowed, params = router.resolve("GET", "/hello/bob")
    assert handler is h
    assert params == {"name": "bob"}