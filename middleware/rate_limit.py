import time
from collections import defaultdict, deque
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


# Og'ir endpointlar uchun qat'iyroq cheklov
STRICT_PATHS = {"/chat", "/diagnostic"}

# Umumiy cheklov: 1 daqiqada 60 so'rov
DEFAULT_LIMIT = 60
DEFAULT_WINDOW = 60  # seconds

# Og'ir endpointlar uchun: 1 daqiqada 10 so'rov
STRICT_LIMIT = 10
STRICT_WINDOW = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # {ip: deque([timestamp, ...])}
        self._default_store: dict[str, deque] = defaultdict(deque)
        self._strict_store: dict[str, deque] = defaultdict(deque)

    def _get_client_ip(self, request: Request) -> str:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _is_allowed(self, store: dict, key: str, limit: int, window: int) -> tuple[bool, int]:
        now = time.time()
        q = store[key]
        # Eski so'rovlarni o'chirish
        while q and q[0] <= now - window:
            q.popleft()
        remaining = max(0, limit - len(q))
        if len(q) >= limit:
            return False, 0
        q.append(now)
        return True, remaining - 1

    async def dispatch(self, request: Request, call_next) -> Response:
        ip = self._get_client_ip(request)
        path = request.url.path

        is_strict = any(path.startswith(p) for p in STRICT_PATHS)

        if is_strict:
            allowed, remaining = self._is_allowed(
                self._strict_store, ip, STRICT_LIMIT, STRICT_WINDOW
            )
            limit_header = str(STRICT_LIMIT)
        else:
            allowed, remaining = self._is_allowed(
                self._default_store, ip, DEFAULT_LIMIT, DEFAULT_WINDOW
            )
            limit_header = str(DEFAULT_LIMIT)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Juda ko'p so'rov yuborildi. Iltimos, biroz kuting."},
                headers={
                    "X-RateLimit-Limit": limit_header,
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": "60",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = limit_header
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
