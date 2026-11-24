from contextlib import asynccontextmanager

from pydantic import BaseModel

from easyapi import EasyAPI, Request, Response, Depends

@asynccontextmanager
async def lifespan(app):
    print("startup: opening resources")
    yield
    print("shutdown: closing resources")


app = EasyAPI(lifespan=lifespan)


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

@app.get("/greet")
async def greet(name: str = "world"):
    return Response(f"Hello, {name}")

@app.get("/add")
async def add(a: int, b: int = 0):
    return Response(str(a + b))

class Item(BaseModel):
    name: str
    price: float

@app.post("/items")
async def create(item: Item):
    return {"name": item.name, "price": item.price}

def get_db():
    return {"connected": True}

@app.get("/users")
async def users(db=Depends(get_db)):
    return {"db": db}

import time

from easyapi import Depends, HTTPException


class TimingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                elapsed = time.perf_counter() - start
                message["headers"] = [
                    *message["headers"],
                    (b"x-process-time", f"{elapsed:.6f}".encode()),
                ]
            await send(message)

        await self.app(scope, receive, send_wrapper)


app.add_middleware(TimingMiddleware)


def require_token(token: str = ""):
    if token != "123":
        raise HTTPException(401, "Invalid token")
    return token

@app.get("/secret")
async def secret(t: str = Depends(require_token)):
    return {"secret": "42"}

@app.get("/slow")
def slow():
    time.sleep(2)
    return {"done": True}