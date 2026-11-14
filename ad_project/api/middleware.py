"""Small security middleware used by the API boundary."""

import time
from collections import defaultdict, deque
from typing import Deque, DefaultDict

from fastapi import Request
from fastapi.responses import JSONResponse

from ad_project.api.config import Settings


class LoginRateLimitMiddleware:
    """Apply a bounded per-IP login limit for a single API process."""

    def __init__(self, app, settings: Settings):
        self.app = app
        self.settings = settings
        self.attempts: DefaultDict[str, Deque[float]] = defaultdict(deque)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        if request.url.path == "/api/v1/auth/login":
            client = request.client.host if request.client else "unknown"
            now = time.monotonic()
            recent = self.attempts[client]
            while recent and now - recent[0] >= 60:
                recent.popleft()
            if len(recent) >= self.settings.login_rate_limit_per_minute:
                response = JSONResponse(
                    status_code=429,
                    content={"error": {"code": "rate_limited", "message": "Too many login attempts"}},
                    headers={"Retry-After": "60"},
                )
                await response(scope, receive, send)
                return
            recent.append(now)
        await self.app(scope, receive, send)
