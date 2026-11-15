import json

import pytest
from fastapi.testclient import TestClient

from api.app.main import app
from frontend.utils.data import serialize_mapping


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client


@pytest.mark.parametrize("number", ["NaN", "Infinity", "1e309"])
def test_nonfinite_error_is_json_422_not_500(client, single_claim, number):
    body = (
        '{"claims":['
        + json.dumps(serialize_mapping(single_claim))
        + '],"review_fraction":'
        + number
        + "}"
    )
    response = client.post(
        "/top-review",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Request-ID": "fixture-nonfinite",
        },
    )
    assert response.status_code == 422
    assert response.json()["detail"]
    assert response.headers["X-Request-ID"] == "fixture-nonfinite"
    assert "input" not in str(response.json())


@pytest.mark.parametrize(
    "field,value",
    [
        ("claim_amount", -1),
        ("requested_reimbursement", 1e8),
        ("customer_claims_7d", -1),
        ("service_date", "2099-01-01"),
        ("provider_type", {"nested": "not scalar"}),
    ],
)
def test_business_contract_rejects_invalid_claims(client, single_claim, field, value):
    record = serialize_mapping(single_claim)
    record[field] = value
    response = client.post("/score", json={"claim": record})
    assert response.status_code == 422


def test_duplicate_json_request_keys_are_rejected(client):
    response = client.post(
        "/score",
        content='{"claim":{},"claim":{}}',
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422


def test_request_id_is_bounded_and_normalized(client):
    response = client.get("/health", headers={"X-Request-ID": "x" * 300})
    assert response.status_code == 200
    assert len(response.headers["X-Request-ID"]) == 32


def test_oversized_stream_is_rejected(client):
    from health_fraud.config import MAX_UPLOAD_BYTES

    response = client.post("/score", content=b" " * (MAX_UPLOAD_BYTES + 1))
    assert response.status_code == 413


def test_smart_intake_roundtrips_through_real_model(client):
    import pandas as pd
    import yaml
    from health_fraud.features.history import _build_smart_claim

    frame = pd.read_parquet("data/interim/claims.parquet")
    frame.attrs["policies"] = pd.read_parquet("data/interim/policies.parquet")
    with open("configs/data.yaml", encoding="utf-8") as file:
        settings = yaml.safe_load(file)
    frame.attrs["coverage_limits"] = settings["policy"]["coverage_limits"]
    frame.attrs["service_priors"] = {
        k: v["amount"]["median"] for k, v in settings["services"].items()
    }
    previous = frame.loc[
        frame.provider_id.notna() & frame.days_since_policy_change.isna()
    ].iloc[-1]
    when = pd.Timestamp(frame.claim_submission_timestamp.max()) + pd.Timedelta(hours=1)
    record = _build_smart_claim(
        history=frame,
        customer_id=str(previous.customer_id),
        provider_id=str(previous.provider_id),
        service_category="consultation",
        service_code="CONS_001",
        service_units=1,
        service_date=when.date(),
        submission_datetime=when.to_pydatetime(),
        claim_amount=100.0,
        requested_reimbursement=80.0,
        submission_channel="web",
        document_count=1,
        has_invoice=True,
        has_prescription=None,
    )
    response = client.post("/score", json={"claim": record})
    assert response.status_code == 200, response.text
    assert 0 <= response.json()["prediction"]["fraud_risk_score"] <= 1
