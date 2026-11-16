"""Bounded request ingestion for the public, account-free inference demo."""

from __future__ import annotations

import asyncio

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from health_fraud.config import MAX_UPLOAD_BYTES
from health_fraud.data.io import strict_json_loads


class RequestBudgetMiddleware:
    def __init__(self, app: ASGIApp, max_inflight: int = 4) -> None:
        self.app = app
        self.slots = asyncio.Semaphore(max_inflight)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["method"] != "POST":
            await self.app(scope, receive, send)
            return
        try:
            await asyncio.wait_for(self.slots.acquire(), timeout=0.25)
        except TimeoutError:
            await JSONResponse(
                {"detail": "Inference capacity is busy; retry shortly."},
                status_code=429,
                headers={"Retry-After": "2"},
            )(scope, receive, send)
            return
        try:
            chunks = []
            length = 0
            while True:
                try:
                    message = await asyncio.wait_for(receive(), timeout=15)
                except TimeoutError:
                    await JSONResponse(
                        {"detail": "Request body timed out."}, status_code=408
                    )(scope, receive, send)
                    return
                if message["type"] == "http.disconnect":
                    return
                chunk = message.get("body", b"")
                length += len(chunk)
                if length > MAX_UPLOAD_BYTES:
                    await JSONResponse(
                        {"detail": "Request exceeds the 16 MiB limit."}, status_code=413
                    )(scope, receive, send)
                    return
                chunks.append(chunk)
                if not message.get("more_body", False):
                    break
            body = b"".join(chunks)
            if body:
                try:
                    strict_json_loads(body)
                except (ValueError, UnicodeError) as exc:
                    await JSONResponse(
                        {
                            "detail": [
                                {
                                    "loc": ["body"],
                                    "msg": str(exc),
                                    "type": "invalid_json",
                                }
                            ]
                        },
                        status_code=422,
                    )(scope, receive, send)
                    return
            replayed = False

            async def replay() -> Message:
                nonlocal replayed
                if not replayed:
                    replayed = True
                    return {"type": "http.request", "body": body, "more_body": False}
                return await receive()

            await self.app(scope, replay, send)
        finally:
            self.slots.release()
