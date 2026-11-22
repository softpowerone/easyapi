from easyapi import EasyAPI, Request, Response

app = EasyAPI()

@app.get("/")
async def index(request: Request) -> Response:
    return Response("Hello World")

@app.get("/ping")
async def ping(request: Request) -> Response:
    return Response("pong")