"""Run the demo with optional co-located, loopback-only FastAPI inference.

The API and Streamlit share one interpreter to avoid duplicating numerical
libraries on the 512 MiB demo instance. Remote inference remains configurable.
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request


def inference_mode() -> str:
    mode = os.environ.get("FRAUD_INFERENCE_MODE", "remote").strip().lower()
    if mode not in {"embedded", "remote"}:
        raise ValueError("FRAUD_INFERENCE_MODE must be embedded or remote.")
    return mode


def wait_for_inference(thread: threading.Thread, url: str, timeout: float = 45) -> None:
    deadline = time.monotonic() + timeout
    while thread.is_alive() and time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url + "/health", timeout=1) as response:
                if json.load(response).get("model_loaded") is True:
                    return
        except (urllib.error.URLError, TimeoutError, ValueError):
            pass
        time.sleep(0.1)
    raise RuntimeError("Demo inference did not become ready before startup completed.")


def main() -> None:
    server = None
    thread = None
    if inference_mode() == "embedded":
        import uvicorn

        # This route never exposes the internal scoring listener publicly.
        os.environ["FRAUD_API_URL"] = "http://127.0.0.1:8800"
        server = uvicorn.Server(uvicorn.Config(
            "api.app.main:app", host="127.0.0.1", port=8800,
            loop="asyncio", log_level="warning", access_log=False,
        ))
        thread = threading.Thread(target=server.run, name="demo-inference", daemon=True)
        thread.start()
        try:
            wait_for_inference(thread, os.environ["FRAUD_API_URL"])
        except BaseException:
            server.should_exit = True
            thread.join(timeout=10)
            raise

    from streamlit.web.cli import main as streamlit_main

    sys.argv = [
        "streamlit", "run", "frontend/app.py", "--server.address=0.0.0.0",
        "--server.port=" + os.environ.get("PORT", "8501"),
        "--server.headless=true", "--server.fileWatcherType=none",
    ]
    try:
        streamlit_main()
    finally:
        if server is not None:
            server.should_exit = True
        if thread is not None:
            thread.join(timeout=10)


if __name__ == "__main__":
    main()
