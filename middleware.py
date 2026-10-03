from __future__ import annotations
import os, time
from collections import defaultdict, deque
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class SafetyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_body_bytes: int = 12 * 1024 * 1024, requests_per_minute: int = 60):
        super().__init__(app); self.max_body_bytes=max_body_bytes; self.limit=requests_per_minute; self.hits=defaultdict(deque)
    async def dispatch(self, request, call_next):
        if request.url.path.startswith('/api/'):
            length = request.headers.get('content-length')
            if length and int(length) > self.max_body_bytes: return JSONResponse({'detail':'Request body too large'}, status_code=413)
            now=time.monotonic(); key=request.client.host if request.client else 'unknown'; q=self.hits[key]
            while q and now-q[0] > 60: q.popleft()
            if len(q) >= self.limit: return JSONResponse({'detail':'Rate limit exceeded'}, status_code=429)
            q.append(now)
        return await call_next(request)
