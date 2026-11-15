"""Point-in-time policy context; dates are used instead of ageing rounded tenures."""

from __future__ import annotations

from typing import Any, Mapping

import pandas as pd

from health_fraud.config import RECENT_POLICY_CHANGE_DAYS


def policy_context(
    latest_claim: pd.Series,
    submitted_at: pd.Timestamp,
    service_category: str,
    policies: pd.DataFrame | None,
    coverage_limits: Mapping[str, Mapping[str, float]] | None,
) -> dict[str, Any]:
    """Resolve an effective contract with explicit fallback provenance.

    A historical snapshot can report a last known change. It cannot establish
    whether another, unrecorded event occurred later. The demonstration exposes
    this limitation instead of silently treating the old snapshot as current.
    """
    policy_id = str(latest_claim.get("policy_id", ""))
    row = None
    if policies is not None and "policy_id" in policies:
        matches = policies.loc[policies["policy_id"].astype(str) == policy_id]
        if len(matches) == 1:
            row = matches.iloc[0]
    level = latest_claim.get("coverage_level")
    tenure = None
    if row is not None:
        start = pd.to_datetime(row.get("policy_start_date"), errors="coerce")
        end = pd.to_datetime(row.get("policy_end_date"), errors="coerce")
        if pd.isna(start) or start > submitted_at:
            raise ValueError("No policy effective at the requested submission date.")
        if pd.notna(end) and submitted_at > end:
            raise ValueError("The selected policy ended before the submission date.")
        tenure = max(1, int((submitted_at - start).days / 30.4375))
        level = row.get("coverage_level", level)
    limit = (coverage_limits or {}).get(str(level), {}).get(service_category)
    if limit is None:
        if str(latest_claim.get("service_category")) != service_category:
            raise ValueError(
                "Coverage for this service is unknown; load the policy limits first."
            )
        limit = latest_claim.get("coverage_limit")
    if limit is None or float(limit) <= 0:
        raise ValueError("A positive effective coverage limit is required.")

    elapsed = None
    origin = "not_recorded"
    event_date = None
    if row is not None and pd.notna(row.get("policy_change_date")):
        event_date = pd.Timestamp(row["policy_change_date"])
        if event_date > submitted_at:
            event_date = None
        else:
            origin = "policy_event"
            level = row.get("new_coverage_level", level)
            limit = (
                (coverage_limits or {}).get(str(level), {}).get(service_category, limit)
            )
    prior_days = latest_claim.get("days_since_policy_change")
    if event_date is None and prior_days is not None and pd.notna(prior_days):
        event_date = pd.Timestamp(
            latest_claim["claim_submission_timestamp"]
        ) - pd.Timedelta(days=float(prior_days))
        origin = "last_known_snapshot"
    if event_date is not None:
        elapsed = max(0.0, (submitted_at - event_date).total_seconds() / 86400)
    return {
        "policy_tenure_months": tenure,
        "coverage_level": level,
        "coverage_limit": float(limit),
        "days_since_policy_change": elapsed,
        "recent_policy_change": int(elapsed <= RECENT_POLICY_CHANGE_DAYS)
        if elapsed is not None
        else None,
        "policy_context_origin": origin,
    }
