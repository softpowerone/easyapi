from easyapi.responses import Response


async def run(response):
    sent = []

    async def send(message):
        sent.append(message)

    await response(send)
    return sent


async def test_order_start_then_body():
    sent = await run(Response("hi"))
    assert [m["type"] for m in sent] == ["http.response.start", "http.response.body"]


async def test_status_and_body():
    sent = await run(Response("hi", status=404))
    assert sent[0]["status"] == 404
    assert sent[1]["body"] == b"hi"


async def test_headers_encoded_as_bytes():
    sent = await run(Response("x", headers={"X-Test": "1"}))
    assert (b"x-test", b"1") in sent[0]["headers"]