from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from unittest.mock import Mock

import pytest
import requests

from frontend.api_client import (
    FraudAPIClient, FraudAPIError, FraudAPIResponseError,
    FraudAPITimeoutError, FraudAPIUnavailableError,
)


@pytest.mark.parametrize("failure,expected", [
    (requests.ConnectTimeout(), FraudAPITimeoutError),
    (requests.ReadTimeout(), FraudAPITimeoutError),
    (requests.ConnectionError(), FraudAPIUnavailableError),
    (requests.RequestException("internal-host-secret"), FraudAPIError),
])
def test_network_errors_are_actionable_without_internal_details(failure, expected):
    with FraudAPIClient("http://127.0.0.1:1") as client:
        client.session.request = Mock(side_effect=failure)
        with pytest.raises(expected) as error:
            client._request("POST", "/score", json={"claim": {}})
        assert "internal-host-secret" not in str(error.value)
        assert client.session.request.call_count == 1


@pytest.mark.parametrize("payload", [None, [], "bad JSON"])
def test_success_http_status_still_requires_a_valid_json_object(payload):
    response = Mock(ok=True, status_code=200)
    response.json = Mock(side_effect=ValueError()) if payload == "bad JSON" else Mock(return_value=payload)
    with FraudAPIClient("http://127.0.0.1:1") as client:
        client.session.request = Mock(return_value=response)
        with pytest.raises(FraudAPIResponseError):
            client._request("GET", "/health")


def test_real_transport_retries_health_but_never_replays_scoring_post():
    counts = {"GET": 0, "POST": 0}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            counts["GET"] += 1
            code = 200 if counts["GET"] == 3 else 503
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Retry-After", "0")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')

        def do_POST(self):
            counts["POST"] += 1
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            self.send_response(503)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"detail":"temporarily busy"}')

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with FraudAPIClient(f"http://127.0.0.1:{server.server_port}") as client:
            assert client._request("GET", "/health") == {"status": "ok"}
            with pytest.raises(FraudAPIResponseError, match="503"):
                client._request("POST", "/score", json={"claim": {}})
        assert counts == {"GET": 3, "POST": 1}
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
