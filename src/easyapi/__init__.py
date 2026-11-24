"""EasyAPI: build an MVP backend in 30 minutes."""

from .applications import EasyAPI
from .responses import Response, JSONResponse
from .requests import Request
from .exeptions import HTTPException
from .dependencies import Depends

__all__ = ["EasyAPI", "Request", "Response", "HTTPException", "JSONResponse", "Depends"]