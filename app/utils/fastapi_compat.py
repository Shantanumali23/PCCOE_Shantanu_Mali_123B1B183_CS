"""
CodeSecure AI — FastAPI Compatibility Shim
Provides standard FastAPI imports when installed, with graceful fallbacks
so that models, core services, and tests run cleanly in lightweight environments.
"""

from typing import Any, Callable, Dict, List, Optional

try:
    from fastapi import FastAPI, Request, APIRouter, Depends, HTTPException, status, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    FASTAPI_AVAILABLE = True

except ImportError:
    FASTAPI_AVAILABLE = False

    class HTTPException(Exception):
        def __init__(self, status_code: int = 400, detail: str = "", headers: Optional[dict] = None):
            self.status_code = status_code
            self.detail = detail
            self.headers = headers
            super().__init__(detail)

    class status:
        HTTP_200_OK = 200
        HTTP_400_BAD_REQUEST = 400
        HTTP_401_UNAUTHORIZED = 401
        HTTP_403_FORBIDDEN = 403
        HTTP_404_NOT_FOUND = 404
        HTTP_500_INTERNAL_SERVER_ERROR = 500

    def Depends(dependency: Optional[Callable] = None):
        return dependency

    def Query(default: Any = None, **kwargs):
        return default

    class HTTPBearer:
        def __init__(self, auto_error: bool = True):
            self.auto_error = auto_error

    class HTTPAuthorizationCredentials:
        def __init__(self, credentials: str = "", scheme: str = "Bearer"):
            self.credentials = credentials
            self.scheme = scheme

    class APIRouter:
        def __init__(self, prefix: str = "", tags: Optional[List[str]] = None):
            self.prefix = prefix
            self.tags = tags or []
            self.routes = []

        def get(self, path: str, **kwargs):
            def decorator(func):
                self.routes.append(("GET", f"{self.prefix}{path}", func))
                return func
            return decorator

        def post(self, path: str, **kwargs):
            def decorator(func):
                self.routes.append(("POST", f"{self.prefix}{path}", func))
                return func
            return decorator

        def patch(self, path: str, **kwargs):
            def decorator(func):
                self.routes.append(("PATCH", f"{self.prefix}{path}", func))
                return func
            return decorator

    class FastAPI:
        def __init__(self, title: str = "", description: str = "", version: str = "", lifespan: Any = None):
            self.title = title
            self.description = description
            self.version = version
            self.lifespan = lifespan
            self.routers = []

        def add_middleware(self, *args, **kwargs):
            pass

        def include_router(self, router: Any):
            self.routers.append(router)

        def get(self, path: str, **kwargs):
            def decorator(func):
                return func
            return decorator

        def post(self, path: str, **kwargs):
            def decorator(func):
                return func
            return decorator

        def exception_handler(self, exc_class: Any):
            def decorator(func):
                return func
            return decorator

    class CORSMiddleware:
        pass

    class Request:
        pass

    class JSONResponse:
        def __init__(self, content: Any = None, status_code: int = 200):
            self.content = content
            self.status_code = status_code
