from easyapi import EasyAPI, Request, Response

app = EasyAPI()

@app.get("/")
async def index(request: Request) -> Response:
    return Response("Hello World")

@app.get("/ping")
async def ping(request: Request) -> Response:
    return Response("pong")

@app.get("/hello/{name}")
async def hello(name: str) -> Response:
    return Response(f"Hello {name}")

@app.get("/square/{n}")
async def square(n: int) -> Response:
    return Response(f"{n * n}")