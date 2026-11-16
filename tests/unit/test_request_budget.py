import asyncio
import json

from api.app.middleware import RequestBudgetMiddleware


def test_streaming_budget_rejects_before_inference_and_releases_slot(monkeypatch):
    monkeypatch.setattr("api.app.middleware.MAX_UPLOAD_BYTES", 100)

    async def check():
        reached = []

        async def app(scope, receive, send):
            reached.append(True)

        middleware = RequestBudgetMiddleware(app, max_inflight=1)
        messages = iter([
            {"type": "http.request", "body": b"x" * 60, "more_body": True},
            {"type": "http.request", "body": b"x" * 41, "more_body": False},
        ])
        sent = []

        async def receive():
            return next(messages)

        async def send(message):
            sent.append(message)

        await middleware({"type": "http", "method": "POST"}, receive, send)
        assert sent[0]["status"] == 413
        assert not reached
        assert not middleware.slots.locked()

    asyncio.run(check())


def test_saturated_inference_returns_retry_after_and_health_stays_available():
    async def check():
        entered, release = asyncio.Event(), asyncio.Event()
        observed = []

        async def app(scope, receive, send):
            if scope["method"] == "POST":
                entered.set()
                await release.wait()
            else:
                observed.append("health")

        middleware = RequestBudgetMiddleware(app, max_inflight=1)

        async def receive():
            return {"type": "http.request", "body": b"{}", "more_body": False}

        sent = []

        async def send(message):
            sent.append(message)

        first = asyncio.create_task(middleware({"type": "http", "method": "POST"}, receive, send))
        await entered.wait()
        await middleware({"type": "http", "method": "GET"}, receive, send)
        await middleware({"type": "http", "method": "POST"}, receive, send)
        assert observed == ["health"]
        assert sent[0]["status"] == 429
        assert (b"retry-after", b"2") in sent[0]["headers"]
        assert "busy" in json.loads(sent[1]["body"])["detail"]
        release.set()
        await first
        assert not middleware.slots.locked()

    asyncio.run(check())
