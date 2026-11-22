from easyapi.requests import Request


def make_request(scope=None, messages=None):
    scope = {"type": "http", "method": "GET", "path": "/", "query_string": b"", "headers": [], **(scope or {})}
    messages = list(messages or [{"type": "http.request", "body": b"", "more_body": False}])

    async def receive():
        return messages.pop(0)

    return Request(scope, receive)


def test_method():
    assert make_request({"method": "POST"}).method == "POST"


def test_path():
    assert make_request({"path": "/hello/world"}).path == "/hello/world"


def test_query_params():
    req = make_request({"query_string": b"x=1&name=bob"})
    assert req.query_params == {"x": "1", "name": "bob"}


def test_headers_lowercase_str():
    req = make_request({"headers": [(b"Content-Type", b"application/json")]})
    assert req.headers == {"content-type": "application/json"}


async def test_body_single_chunk():
    req = make_request(messages=[{"type": "http.request", "body": b"hello", "more_body": False}])
    assert await req.body() == b"hello"


async def test_body_in_chunks():
    req = make_request(messages=[
        {"type": "http.request", "body": b"hel", "more_body": True},
        {"type": "http.request", "body": b"lo", "more_body": False},
    ])
    assert await req.body() == b"hello"