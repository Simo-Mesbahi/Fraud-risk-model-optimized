"""Exercise the real product handoff with real scoring and a deterministic HTTP adapter."""
from urllib.parse import urlsplit
from pathlib import Path

import requests
from fastapi.testclient import TestClient
from streamlit.testing.v1 import AppTest

from api.app.main import app as api
from tests.integration.test_frontend_api_contract import RequestsCompatibleResponse


def test_claim_portfolio_and_investigation_are_one_coherent_workflow(monkeypatch):
    with TestClient(api) as backend:
        def request(self, method, url, **kwargs):
            kwargs.pop("timeout", None)
            return RequestsCompatibleResponse(backend.request(method, urlsplit(url).path, **kwargs))
        monkeypatch.setattr(requests.Session, "request", request)
        ui = AppTest.from_file(Path(__file__).resolve().parents[2] / "frontend/app.py").run(timeout=60)
        assert not ui.exception
        assert len([m for m in ui.markdown if '<h1 ' in m.value]) == 1
        next(button for button in ui.button if button.label == "Try a claim demo").click().run(timeout=60)
        assert ui.radio(key="claim_analysis_mode").value == "Quick Demo"
        ui.button(key="analyze_demo_claim").click().run(timeout=60)
        assert not ui.exception
        assert ui.session_state["single_explanation"]["consistency"]["shap_additivity_ok"] is True
        next(button for button in ui.button if button.label == "Score a portfolio").click().run(timeout=60)
        ui.button(key="score_demo_portfolio").click().run(timeout=60)
        assert not ui.exception
        count = len(ui.session_state["batch_input"])
        assert count == 500
        next(button for button in ui.button if button.label == "Continue to investigation").click().run(timeout=60)
        assert ui.session_state["main_navigation"] == "Investigation Queue"
        next(button for button in ui.button if button.label == "Build queue from scored portfolio").click().run(timeout=60)
        assert not ui.exception
        assert len(ui.session_state["queue_results"]) == 15
        assert len(ui.session_state["queue_source_claims"]) == count
