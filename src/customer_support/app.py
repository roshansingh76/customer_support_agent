import uvicorn
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from .middleware import JWTAuthMiddleware
from .router import api_router

_API_PREFIX = "/api/v1"
_PUBLIC_PATHS = {
    "/api/v1/auth/login",
    "/api/v1/auth/register",
}
_HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}


def create_app() -> FastAPI:
    app = FastAPI(title="Customer Support API")
    app.add_middleware(JWTAuthMiddleware)

    app.include_router(api_router, prefix="/api/v1")

    def custom_openapi() -> dict[str, Any]:
        if app.openapi_schema is not None:
            return app.openapi_schema

        schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            routes=app.routes,
        )
        schema.setdefault("components", {}).setdefault("securitySchemes", {})[
            "BearerAuth"
        ] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }

        for path, path_item in schema.get("paths", {}).items():
            is_api_request = path == _API_PREFIX or path.startswith(f"{_API_PREFIX}/")
            if not is_api_request or path in _PUBLIC_PATHS:
                continue
            for method, operation in path_item.items():
                if method in _HTTP_METHODS and isinstance(operation, dict):
                    operation["security"] = [{"BearerAuth": []}]

        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = custom_openapi

    @app.get("/health", tags=["Health"])
    def health_check() -> dict:
        return {
            "status": 200,
            "message": "success",
        }

    return app

app = create_app()


def main() -> None:
    uvicorn.run(
        "customer_support.app:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    main()
