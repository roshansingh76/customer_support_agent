import jwt
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from .services.security import decode_access_token

_API_PREFIX = "/api/v1"
_PUBLIC_PATHS = {
    "/api/v1/auth/login",
    "/api/v1/auth/register",
}


class JWTAuthMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope["path"]
        is_api_request = path == _API_PREFIX or path.startswith(f"{_API_PREFIX}/")
        if not is_api_request or path in _PUBLIC_PATHS:
            await self.app(scope, receive, send)
            return

        authorization_headers = [
            value
            for name, value in scope.get("headers", [])
            if name.lower() == b"authorization"
        ]
        if len(authorization_headers) != 1:
            await self._unauthorized(scope, receive, send)
            return

        parts = authorization_headers[0].split()
        if len(parts) != 2 or parts[0].lower() != b"bearer":
            await self._unauthorized(scope, receive, send)
            return

        try:
            token = parts[1].decode("ascii")
            claims = decode_access_token(token)
        except (UnicodeDecodeError, jwt.InvalidTokenError):
            await self._unauthorized(scope, receive, send)
            return

        subject = claims.get("sub")
        if not isinstance(subject, str) or not subject:
            await self._unauthorized(scope, receive, send)
            return

        scope.setdefault("state", {})["user_email"] = subject
        await self.app(scope, receive, send)

    @staticmethod
    async def _unauthorized(scope: Scope, receive: Receive, send: Send) -> None:
        response = JSONResponse(
            status_code=401,
            content={"message": "Not authenticated"},
            headers={"WWW-Authenticate": "Bearer"},
        )
        await response(scope, receive, send)
