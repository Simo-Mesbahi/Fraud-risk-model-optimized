"""Vectorized quality evidence; structural missingness is not labelled corruption."""

from __future__ import annotations

import numpy as np
import pandas as pd

STRUCTURAL_MISSING = {
    "days_since_policy_change",
    "days_since_customer_previous_claim",
    "days_since_same_provider_claim",
    "customer_avg_claim_amount_365d",
    "provider_avg_claim_amount_90d",
    "claim_to_customer_avg_ratio",
    "claim_to_provider_avg_ratio",
}


def quality_profile(frame: pd.DataFrame) -> dict:
    n = len(frame)
    columns = []
    for name in frame:
        series = frame[name]
        missing = int(series.isna().sum())
        columns.append(
            {
                "column": name,
                "dtype": str(series.dtype),
                "missing": missing,
                "missing_rate": missing / n if n else 0,
                "distinct": int(series.nunique(dropna=True)),
                "missingness_context": "May represent absent historical evidence"
                if name in STRUCTURAL_MISSING
                else "Inspect source and business rules",
            }
        )
    issues = {}
    if "claim_id" in frame:
        issues["duplicate_claim_ids"] = int(frame.claim_id.duplicated().sum())
    for name in [
        "claim_amount",
        "requested_reimbursement",
        "coverage_limit",
        "service_units",
        "document_count",
    ]:
        if name in frame:
            numeric = pd.to_numeric(frame[name], errors="coerce")
            issues[f"negative_{name}"] = int((numeric < 0).sum())
            issues[f"nonfinite_{name}"] = int(
                (numeric.notna() & ~np.isfinite(numeric)).sum()
            )
    if {"service_date", "claim_submission_timestamp"}.issubset(frame):
        service = pd.to_datetime(frame.service_date, errors="coerce")
        submitted = pd.to_datetime(frame.claim_submission_timestamp, errors="coerce")
        issues["invalid_dates"] = int((service.isna() | submitted.isna()).sum())
        issues["service_after_submission"] = int(
            (service.dt.normalize() > submitted.dt.normalize()).sum()
        )
    if {"claim_amount", "requested_reimbursement", "coverage_limit"}.issubset(frame):
        issues["reimbursement_above_limit"] = int(
            (frame.requested_reimbursement > frame.coverage_limit + 0.01).sum()
        )
        issues["reimbursement_above_claim"] = int(
            (frame.requested_reimbursement > frame.claim_amount + 0.01).sum()
        )
    return {
        "rows": n,
        "columns": len(frame.columns),
        "rows_with_missing_values": int(frame.isna().any(axis=1).sum()),
        "rules": issues,
        "column_profile": columns,
    }


def distribution_shift(reference: pd.Series, current: pd.Series, bins=10) -> dict:
    """Reference-quantile PSI with explicit sample sizes and smoothing."""
    before = pd.to_numeric(reference, errors="coerce").dropna().to_numpy()
    after = pd.to_numeric(current, errors="coerce").dropna().to_numpy()
    if len(before) < 20 or len(after) < 20:
        return {"psi": None, "reference": len(before), "current": len(after)}
    edges = np.unique(np.quantile(before, np.linspace(0, 1, bins + 1)))
    if len(edges) < 3:
        return {"psi": None, "reference": len(before), "current": len(after)}
    edges[0], edges[-1] = -np.inf, np.inf
    p = np.histogram(before, edges)[0].astype(float) + 0.5
    q = np.histogram(after, edges)[0].astype(float) + 0.5
    p /= p.sum()
    q /= q.sum()
    return {
        "psi": float(np.sum((q - p) * np.log(q / p))),
        "reference": len(before),
        "current": len(after),
    }
