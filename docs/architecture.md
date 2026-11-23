# Architecture

EasyAPI is a lightweight ASGI framework for building MVP backends quickly. This document describes how the codebase is organized and how a request moves through it.

## Layers

```
Server (uvicorn)   accepts connections, parses HTTP, calls the ASGI app
EasyAPI            routing, parameter binding, validation, dependencies, middleware
```

EasyAPI does not implement an HTTP server. It is a standard ASGI application: any ASGI server can run it.

## Modules

| Module | Responsibility |
| --- | --- |
| `_types.py` | ASGI types (`Scope`, `Message`, `Receive`, `Send`) and the `Handler` type. |
| `requests.py` | `Request`: method, path, query parameters, headers, body (cached after the first read). |
| `responses.py` | `Response`, `JSONResponse`, `make_response`. |
| `routing.py` | `Router`: route registration, path templates such as `/hello/{name}`, handler lookup, 404/405 detection. |
| `params.py` | `convert` and `build_kwargs`: builds handler arguments from its signature (request, path, query, Pydantic body, `Depends`). |
| `dependencies.py` | `Depends`: dependency marker. |
| `exceptions.py` | `HTTPException`. |
| `applications.py` | `EasyAPI`: ties the parts together, implements the ASGI interface, manages middleware. |
| `__init__.py` | Public API (`__all__`). |

## Dependency rule

Imports point only downwards. A module may import from modules below it, never from modules above it. This prevents circular imports.

```
applications → routing
applications → params
applications → requests
applications → responses
applications → exceptions
applications → _types

params       → requests
params       → dependencies
params       → _types

routing      → _types
requests     → _types
responses    → _types

dependencies → (nothing from the project)
exceptions   → (nothing from the project)
_types       → (nothing from the project)
```

Levels, bottom to top:

1. `_types`, `dependencies`, `exceptions`: no project imports.
2. `requests`, `responses`, `routing`: depend only on `_types`.
3. `params`: depends on `requests`, `dependencies`, `_types`.
4. `applications`: depends on everything below.

The router only resolves a handler and returns `(handler, allowed_methods, path_params)`. Building responses for 404 and 405 is the job of `applications`, so `routing` does not import `responses` or `requests`.

## Request lifecycle

```
Client → server → app(scope, receive, send)
                     │
                Middleware chain
                     │
                  _dispatch → Request(scope, receive)
                     │
             Router.resolve(method, path)
                     │
       ┌─────────────┼─────────────┐
     404           405          handler found
                                    │
                             build_kwargs
                  ┌─────────┬───────┼─────────┬──────────┐
               request    path    query     body        Depends
                                            (Pydantic)  (recursive, cached)
                                    │
                             await handler(**kwargs)
                                    │
                             make_response
                      (Response as is, otherwise JSONResponse)
                                    │
                                send(...)
```

## Parameter binding

`build_kwargs` inspects the handler signature (`inspect.signature`) and type hints (`typing.get_type_hints`) and fills each parameter in this order:

1. A parameter named `request` receives the `Request`.
2. A parameter whose default is `Depends(...)` receives the dependency result. Dependencies are resolved recursively and cached per request, so each one runs at most once.
3. A parameter annotated with a Pydantic model is parsed and validated from the JSON body.
4. A parameter that matches a path template variable is taken from the URL and converted to the annotated type.
5. A parameter that matches a query string key is taken from the query and converted to the annotated type.
6. A parameter with no source and no default value is an error (422).

Parameters with a default value that were not supplied are left out, and Python applies the default.

## Responses and errors

A handler may return a `Response` (sent as is) or any JSON-serializable value (wrapped in `JSONResponse` with status 200).

Error responses use the format `{"detail": ...}`:

| Situation | Status |
| --- | --- |
| No matching path | 404 |
| Path matches, method does not (`Allow` header is set) | 405 |
| Invalid or missing parameters, invalid body | 422 |
| `HTTPException` raised in a handler or dependency | the exception's status |
| Any other unhandled exception (logged with traceback) | 500 |

## Middleware

A middleware is any callable that takes an ASGI app and returns an ASGI app. `app.add_middleware(MiddlewareClass, **options)` wraps the current stack, so the last middleware added is the outermost one and sees the request first.

## Testing

Application-level tests call the app directly through `httpx.ASGITransport`, without starting a server. Unit tests for `Request`, `Response` and `Router` use hand-written `receive` and `send` callables.

## Known limitations

- Type conversion supports `int`, `float`, `bool`, `str` and Pydantic models. `Optional[...]` and `X | None` annotations are not converted yet.
- Path templates are matched in registration order. Register specific routes (`/users/me`) before general ones (`/users/{id}`).
- `content-length` is not set explicitly; the server handles it.
- Dependencies with `yield` are not supported.
- Custom exception handlers (`@app.exception_handler`) are not supported.
- Exceptions raised inside middleware itself are not caught by the framework.
- Synchronous handlers and dependencies are not supported yet.

## Roadmap

**v0.1 (core)**

- [x] ASGI application
- [x] `Request` and `Response`
- [x] Router with 404/405
- [x] Path and query parameters
- [x] Automatic JSON responses
- [x] Pydantic request bodies
- [x] `Depends`
- [ ] `HTTPException`, JSON errors, middleware
- [ ] Sync handlers via a thread pool
- [ ] Lifespan (startup/shutdown)
- [ ] Documentation, CI, release to PyPI

**After v0.1**

Database layer with automatic schema updates, automatic CRUD (`app.crud(Model)`), authentication (`app.enable_auth()`), OpenAPI/Swagger documentation, CLI.
