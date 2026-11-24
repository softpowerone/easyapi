# easyapix
[![CI](https://github.com/softpowerone/easyapix/actions/workflows/ci.yml/badge.svg)](https://github.com/softpowerone/easyapix/actions/workflows/ci.yml)
Lightweight ASGI framework for building MVP backends quickly.

> Status: alpha. The API may change before 1.0.
> Not to be confused with the unrelated easyapi package on PyPI, an old package created in 2014 that has not been updated since.

## Install

```bash
pip install easyapix
```

Requires Python 3.10+.

## Quick start

```python
from pydantic import BaseModel

from easyapix import Depends, EasyAPIx, HTTPException

app = EasyAPIx()


class Item(BaseModel):
    name: str
    price: float


def get_db():
    return {"connected": True}


@app.get("/")
async def index():
    return {"message": "Hello, world"}


@app.get("/users/{id}")
async def get_user(id: int, verbose: bool = False):
    if id > 100:
        raise HTTPException(404, "User not found")
    return {"id": id, "verbose": verbose}


@app.post("/items")
async def create_item(item: Item, db=Depends(get_db)):
    return {"name": item.name, "price": item.price, "db": db}
```

Run it:

```bash
uvicorn main:app --reload
```

## Features

- Routing: `get`, `post`, `put`, `patch`, `delete`
- Path and query parameters with type conversion
- Automatic JSON responses
- Pydantic request bodies with validation errors
- Dependency injection with `Depends`
- `HTTPException` and JSON error responses
- Middleware
- Sync and async handlers
- Lifespan (startup/shutdown)

## Documentation

- [Architecture](docs/architecture.md)
- [Examples](examples/)
- [Changelog](CHANGELOG.md)

## License

MIT