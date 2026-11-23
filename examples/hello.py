from pydantic import BaseModel

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