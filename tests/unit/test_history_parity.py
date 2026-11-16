from datetime import datetime

import pandas as pd
import pytest

from health_fraud.data.generate import add_historical_features
from health_fraud.features.history import _build_smart_claim
from health_fraud.features.policy import policy_context


def history_frame():
    rows = []
    for i, code in enumerate(["CONS_001", "CONS_002", "CONS_001"]):
        rows.append(
            dict(
                claim_id=f"DUMMY_{i}",
                customer_id="C",
                provider_id="P",
                policy_id="POL",
                service_category="consultation",
                service_code=code,
                claim_submission_timestamp=pd.Timestamp("2026-01-01")
                + pd.Timedelta(days=i),
                claim_amount=100.0,
                coverage_limit=500.0,
                customer_age=30,
                customer_tenure_months=12,
                coverage_level="basic",
                policy_tenure_months=6,
                recent_policy_change=True,
                days_since_policy_change=20.0,
                provider_type="clinic",
                provider_region="test",
                provider_tenure_months=12,
            )
        )
    return pd.DataFrame(rows)


def smart(frame, when=datetime(2026, 1, 3)):
    return _build_smart_claim(
        history=frame,
        customer_id="C",
        provider_id="P",
        service_category="consultation",
        service_code="CONS_001",
        service_units=1,
        service_date=when.date(),
        submission_datetime=when,
        claim_amount=100.0,
        requested_reimbursement=80.0,
        submission_channel="web",
        document_count=1,
        has_invoice=True,
        has_prescription=False,
    )


def test_same_service_definition_matches_offline_generation():
    frame = history_frame()
    offline = add_historical_features(
        frame, {"services": {"consultation": {"amount": {"median": 100}}}}
    )
    online = smart(frame.iloc[:2])
    assert (
        offline.iloc[2].same_service_claims_30d
        == online["same_service_claims_30d"]
        == 2
    )
    assert offline.iloc[2].customer_claims_30d == online["customer_claims_30d"] == 2


def test_future_claims_do_not_change_smart_features():
    frame = history_frame()
    extra = frame.iloc[-1:].copy()
    extra["claim_submission_timestamp"] = pd.Timestamp("2030-01-01")
    extra["claim_amount"] = 999999.0
    first = smart(frame.iloc[:2])
    second = smart(pd.concat([frame.iloc[:2], extra]))
    first.pop("claim_id")
    second.pop("claim_id")
    assert first == second


def test_policy_tenure_uses_start_date_and_change_snapshot_is_aged():
    latest = history_frame().iloc[0]
    policies = pd.DataFrame(
        [
            dict(
                policy_id="POL",
                policy_start_date=pd.Timestamp("2025-06-01"),
                policy_end_date=pd.NaT,
                coverage_level="basic",
            )
        ]
    )
    when = pd.Timestamp("2026-04-11")
    context = policy_context(
        latest, when, "consultation", policies, {"basic": {"consultation": 100}}
    )
    assert context["policy_tenure_months"] == int(
        (when - pd.Timestamp("2025-06-01")).days / 30.4375
    )
    assert context["days_since_policy_change"] == 120
    assert context["recent_policy_change"] == 0
    assert context["coverage_limit"] == 100
    assert context["policy_context_origin"] == "last_known_snapshot"


def test_missing_policy_dates_are_not_invented_from_rounded_tenure():
    result = policy_context(
        history_frame().iloc[0], pd.Timestamp("2026-04-11"), "consultation", None, None
    )
    assert result["policy_tenure_months"] is None


def test_new_service_requires_its_actual_coverage():
    with pytest.raises(ValueError, match="Coverage"):
        policy_context(
            history_frame().iloc[0], pd.Timestamp("2026-04-11"), "dental", None, None
        )


def test_exact_timestamp_is_excluded_and_left_boundary_is_included():
    frame = history_frame()
    frame.loc[0, "claim_submission_timestamp"] = pd.Timestamp("2025-12-04")
    result = smart(frame, datetime(2026, 1, 3))
    assert result["customer_claims_30d"] == 2


def test_absent_customer_history_fails_with_an_explicit_message():
    frame = history_frame()
    frame["customer_id"] = "OTHER"
    with pytest.raises(ValueError, match="No historical context"):
        smart(frame)


def test_simultaneous_claims_cannot_observe_each_other():
    frame = history_frame()
    frame.loc[1, "claim_submission_timestamp"] = frame.loc[
        0, "claim_submission_timestamp"
    ]
    frame.attrs["service_priors"] = {"consultation": 80.0}
    offline = add_historical_features(
        frame, {"services": {"consultation": {"amount": {"median": 80}}}}
    )
    assert offline.customer_claims_30d.tolist() == [0, 0, 2]
    assert (
        offline.service_typical_amount.iloc[0]
        == offline.service_typical_amount.iloc[1]
        == 80
    )


def test_empty_historical_windows_preserve_missing_means():
    frame = history_frame().iloc[:1]
    result = smart(frame, datetime(2028, 1, 3))
    assert result["customer_claims_365d"] == 0
    assert result["customer_avg_claim_amount_365d"] is None
    assert result["claim_to_customer_avg_ratio"] is None
