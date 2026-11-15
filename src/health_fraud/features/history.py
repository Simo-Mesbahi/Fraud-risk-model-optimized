"""Canonical point-in-time features shared by claim intake and research tests.

No future claim is inspected. Monetary history uses the frozen model's exact
category/code definitions. Entity policy context is attached by the data loader.
"""

from __future__ import annotations
import uuid
from datetime import date, datetime
from typing import Any
import numpy as np
import pandas as pd
from health_fraud.config import LEAKAGE_COLUMNS
from health_fraud.features.policy import policy_context


def _relative_amount(amount: float, reference: float | None) -> float | None:
    return amount / reference if reference is not None and reference > 0 else None


def _rolling_feature(df, group_columns, value_column, window, aggregation):
    """Vectorized grouped windows; no per-entity Python rolling loop."""
    keys = [group_columns] if isinstance(group_columns, str) else list(group_columns)
    ordered = df.sort_values(
        keys + ["claim_submission_timestamp"], kind="mergesort"
    ).copy()
    ordered["_historical_value"] = (
        ordered[value_column].notna().astype(float)
        if aggregation == "count"
        else pd.to_numeric(ordered[value_column], errors="coerce")
    )
    rolling = ordered.groupby(keys, sort=False, dropna=False, observed=True).rolling(
        window, on="claim_submission_timestamp", closed="left"
    )["_historical_value"]
    method = "sum" if aggregation == "count" else aggregation
    if method not in {"sum", "mean", "median"}:
        raise ValueError(f"Unsupported rolling aggregation: {aggregation}")
    result = pd.Series(getattr(rolling, method)().to_numpy(), index=ordered.index)
    # pandas' row-wise rolling can include an earlier row at the identical
    # timestamp. All simultaneous claims must see the same strictly past state.
    buckets = ordered[keys + ["claim_submission_timestamp"]].assign(_value=result)
    lookup = buckets.drop_duplicates(keys + ["claim_submission_timestamp"]).set_index(
        keys + ["claim_submission_timestamp"]
    )["_value"]
    result = pd.Series(
        lookup.reindex(
            pd.MultiIndex.from_frame(buckets[keys + ["claim_submission_timestamp"]])
        ).to_numpy(),
        index=ordered.index,
    ).reindex(df.index)
    return result.fillna(0.0) if aggregation in {"sum", "count"} else result


def _safe_float(value: Any, default: float = 0.0) -> float:
    """
    Convert a value to a finite float.
    """
    try:
        result = float(value)
        if np.isfinite(result):
            return result
    except (TypeError, ValueError):
        pass
    return float(default) if default is not None else None


def _safe_int(value: Any, default: int = 0) -> int:
    """
    Convert numeric-like values to integer safely.
    """
    try:
        if pd.isna(value):
            return default
        return int(round(float(value)))
    except (TypeError, ValueError):
        return default


def _safe_optional_float(value: Any) -> float | None:
    """
    Convert a value to float while preserving missing values.
    """
    try:
        if pd.isna(value):
            return None
        result = float(value)
        if np.isfinite(result):
            return result
    except (TypeError, ValueError):
        pass
    return None


def _safe_bool(value: Any, default: bool = False) -> bool:
    """
    Convert heterogeneous boolean representations safely.
    """
    if value is None:
        return default
    try:
        if pd.isna(value):
            return default
    except (TypeError, ValueError):
        pass
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "y"}
    return bool(value)


def _json_safe(value: Any) -> Any:
    """
    Convert pandas / numpy / datetime values into JSON-safe values.
    """
    if value is None:
        return None
    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if hasattr(value, "item"):
        try:
            return _json_safe(value.item())
        except Exception:
            pass
    return value


def _new_claim_id() -> str:
    """
    Generate an identifier for a new live inference request.
    """
    return "LIVE_" + uuid.uuid4().hex[:12].upper()


def _strip_leakage(claim: dict[str, Any]) -> dict[str, Any]:
    """
    Remove target/generation variables that must never enter inference.
    """
    return {
        key: _json_safe(value)
        for key, value in claim.items()
        if key not in LEAKAGE_COLUMNS
    }


def _history_before(claims: pd.DataFrame, timestamp: pd.Timestamp) -> pd.DataFrame:
    """
    Restrict historical context strictly to information available
    before the current claim.
    """
    return claims.loc[claims["claim_submission_timestamp"] < timestamp]


def _latest_row(frame: pd.DataFrame) -> pd.Series | None:
    """
    Return the most recent historical row.
    """
    if frame.empty:
        return None
    return frame.sort_values("claim_submission_timestamp").iloc[-1]


def _window(frame: pd.DataFrame, timestamp: pd.Timestamp, days: int) -> pd.DataFrame:
    """
    Restrict data to a trailing historical window.
    """
    if frame.empty:
        return frame
    lower = timestamp - pd.Timedelta(days=days)
    mask = (frame["claim_submission_timestamp"] >= lower) & (
        frame["claim_submission_timestamp"] < timestamp
    )
    return frame.loc[mask]


def _amount_values(frame: pd.DataFrame) -> pd.Series:
    """
    Return valid numerical claim amounts.
    """
    if frame.empty or "claim_amount" not in frame.columns:
        return pd.Series(dtype=float)
    return pd.to_numeric(frame["claim_amount"], errors="coerce").dropna()


def _amount_sum(frame: pd.DataFrame) -> float:
    """
    Sum claim amounts safely.
    """
    values = _amount_values(frame)
    if values.empty:
        return 0.0
    return float(values.sum())


def _amount_mean(frame: pd.DataFrame, default: float | None) -> float | None:
    """
    Compute historical mean amount with safe fallback.
    """
    values = _amount_values(frame)
    if values.empty:
        return float(default) if default is not None else None
    return float(values.mean())


def _amount_median(frame: pd.DataFrame, default: float | None) -> float | None:
    """
    Compute historical median amount with safe fallback.
    """
    values = _amount_values(frame)
    if values.empty:
        return float(default) if default is not None else None
    return float(values.median())


def _days_since_last(frame: pd.DataFrame, timestamp: pd.Timestamp) -> float | None:
    """
    Calculate elapsed days since the latest previous claim.
    """
    if frame.empty:
        return None
    dates = frame["claim_submission_timestamp"].dropna()
    dates = dates[dates < timestamp]
    if dates.empty:
        return None
    delta = timestamp - dates.max()
    return max(0.0, float(delta.total_seconds() / 86400))


def _build_smart_claim(
    *,
    history: pd.DataFrame,
    customer_id: str,
    provider_id: str,
    service_category: str,
    service_code: str,
    service_units: int,
    service_date: date,
    submission_datetime: datetime,
    claim_amount: float,
    requested_reimbursement: float,
    submission_channel: str,
    document_count: int,
    has_invoice: bool,
    has_prescription: bool | None,
) -> dict[str, Any]:
    """
    Enrich a minimal operational claim with historical model features.

    Only information available before submission_datetime is used.
    """
    submission_ts = pd.Timestamp(submission_datetime)
    service_ts = pd.Timestamp(service_date)
    if service_ts.normalize() > submission_ts.normalize():
        raise ValueError("Service date cannot occur after the claim submission date.")
    if claim_amount <= 0:
        raise ValueError("Claim amount must be positive.")
    if requested_reimbursement < 0:
        raise ValueError("Requested reimbursement cannot be negative.")
    historical = _history_before(history, submission_ts)
    customer_history = historical.loc[
        historical["customer_id"].astype(str) == str(customer_id)
    ].copy()
    provider_history = historical.loc[
        historical["provider_id"].astype(str) == str(provider_id)
    ].copy()
    relationship_history = customer_history.loc[
        customer_history["provider_id"].astype(str) == str(provider_id)
    ].copy()
    same_service_history = customer_history.loc[
        customer_history["service_category"].astype(str) == str(service_category)
    ].copy()
    service_history = historical.loc[
        historical["service_code"].astype(str) == str(service_code)
    ].copy()
    customer_latest = _latest_row(customer_history)
    provider_latest = _latest_row(provider_history)
    if customer_latest is None:
        raise ValueError(
            f"No historical context exists for customer {customer_id} before the selected submission date."
        )
    if provider_latest is None:
        raise ValueError(
            f"No historical context exists for provider {provider_id} before the selected submission date."
        )
    customer_7d = _window(customer_history, submission_ts, 7)
    customer_30d = _window(customer_history, submission_ts, 30)
    customer_90d = _window(customer_history, submission_ts, 90)
    customer_365d = _window(customer_history, submission_ts, 365)
    provider_30d = _window(provider_history, submission_ts, 30)
    provider_90d = _window(provider_history, submission_ts, 90)
    relationship_30d = _window(relationship_history, submission_ts, 30)
    same_service_30d = _window(same_service_history, submission_ts, 30)
    service_typical_amount = _amount_median(
        service_history,
        default=history.attrs.get("service_priors", {}).get(service_category),
    )
    customer_avg_amount = _amount_mean(customer_365d, default=None)
    provider_avg_amount = _amount_mean(provider_90d, default=None)
    eps = 1e-06
    policy = policy_context(
        customer_latest,
        submission_ts,
        service_category,
        history.attrs.get("policies"),
        history.attrs.get("coverage_limits"),
    )
    coverage_limit = policy["coverage_limit"]
    days_since_policy_change = policy["days_since_policy_change"]
    if requested_reimbursement > min(claim_amount, coverage_limit) + 0.01:
        raise ValueError(
            "Requested reimbursement cannot exceed the claim amount or effective coverage limit."
        )
    claim = {
        "claim_id": _new_claim_id(),
        "customer_id": str(customer_id),
        "policy_id": _json_safe(customer_latest.get("policy_id")),
        "provider_id": str(provider_id),
        "service_category": str(service_category),
        "service_code": str(service_code),
        "service_units": int(service_units),
        "service_date": service_date.isoformat(),
        "claim_submission_date": submission_datetime.date().isoformat(),
        "claim_submission_timestamp": submission_datetime.isoformat(),
        "claim_amount": float(claim_amount),
        "requested_reimbursement": float(requested_reimbursement),
        "coverage_limit": float(coverage_limit),
        "submission_channel": str(submission_channel),
        "document_count": int(document_count),
        "has_invoice": int(bool(has_invoice)),
        "has_prescription": has_prescription,
        "customer_age": _safe_int(customer_latest.get("customer_age")),
        "customer_tenure_months": _safe_int(
            customer_latest.get("customer_tenure_months")
        ),
        "coverage_level": policy["coverage_level"],
        "policy_tenure_months": policy["policy_tenure_months"],
        "recent_policy_change": policy["recent_policy_change"],
        "days_since_policy_change": days_since_policy_change,
        "provider_type": _json_safe(provider_latest.get("provider_type")),
        "provider_region": _json_safe(provider_latest.get("provider_region")),
        "provider_tenure_months": _safe_int(
            provider_latest.get("provider_tenure_months")
        ),
        "days_service_to_submission": int(
            max(0, (submission_ts.normalize() - service_ts.normalize()).days)
        ),
        "reimbursement_ratio": float(requested_reimbursement / max(claim_amount, eps)),
        "customer_claims_7d": len(customer_7d),
        "customer_claims_30d": len(customer_30d),
        "customer_claims_90d": len(customer_90d),
        "customer_claims_365d": len(customer_365d),
        "customer_amount_30d": _amount_sum(customer_30d),
        "customer_amount_365d": _amount_sum(customer_365d),
        "customer_avg_claim_amount_365d": customer_avg_amount,
        "days_since_customer_previous_claim": _days_since_last(
            customer_history, submission_ts
        ),
        "days_since_same_provider_claim": _days_since_last(
            relationship_history, submission_ts
        ),
        "customer_provider_claims_30d": len(relationship_30d),
        "same_service_claims_30d": len(same_service_30d),
        "provider_claims_30d": len(provider_30d),
        "provider_claims_90d": len(provider_90d),
        "provider_avg_claim_amount_90d": provider_avg_amount,
        "service_typical_amount": service_typical_amount,
        "claim_to_service_median_ratio": _relative_amount(
            claim_amount, service_typical_amount
        ),
        "claim_to_customer_avg_ratio": _relative_amount(
            claim_amount, customer_avg_amount
        ),
        "claim_to_provider_avg_ratio": _relative_amount(
            claim_amount, provider_avg_amount
        ),
    }
    claim["policy_context_origin"] = policy["policy_context_origin"]
    return _strip_leakage(claim)


def add_historical_features(
    claims: pd.DataFrame, config: dict[str, Any]
) -> pd.DataFrame:
    df = (
        claims.sort_values("claim_submission_timestamp", kind="mergesort")
        .reset_index(drop=True)
        .copy()
    )
    for window in (7, 30, 90, 365):
        df[f"customer_claims_{window}d"] = _rolling_feature(
            df, "customer_id", "claim_id", f"{window}D", "count"
        )
    df["customer_amount_30d"] = _rolling_feature(
        df, "customer_id", "claim_amount", "30D", "sum"
    )
    df["customer_amount_365d"] = _rolling_feature(
        df, "customer_id", "claim_amount", "365D", "sum"
    )
    df["customer_avg_claim_amount_365d"] = _rolling_feature(
        df, "customer_id", "claim_amount", "365D", "mean"
    )
    df["days_since_customer_previous_claim"] = _strict_previous_days(
        df, ["customer_id"]
    )
    df["days_since_same_provider_claim"] = _strict_previous_days(
        df, ["customer_id", "provider_id"]
    )
    df["customer_provider_claims_30d"] = _rolling_feature(
        df, ["customer_id", "provider_id"], "claim_id", "30D", "count"
    )
    df["same_service_claims_30d"] = _rolling_feature(
        df, ["customer_id", "service_category"], "claim_id", "30D", "count"
    )
    df["provider_claims_30d"] = _rolling_feature(
        df, "provider_id", "claim_id", "30D", "count"
    )
    df["provider_claims_90d"] = _rolling_feature(
        df, "provider_id", "claim_id", "90D", "count"
    )
    df["provider_avg_claim_amount_90d"] = _rolling_feature(
        df, "provider_id", "claim_amount", "90D", "mean"
    )
    historical_service_median = df.groupby("service_code")["claim_amount"].transform(
        lambda series: series.shift(1).expanding().median()
    )
    buckets = df[["service_code", "claim_submission_timestamp"]].assign(
        _value=historical_service_median
    )
    lookup = buckets.drop_duplicates(
        ["service_code", "claim_submission_timestamp"]
    ).set_index(["service_code", "claim_submission_timestamp"])["_value"]
    historical_service_median = pd.Series(
        lookup.reindex(
            pd.MultiIndex.from_frame(
                buckets[["service_code", "claim_submission_timestamp"]]
            )
        ).to_numpy(),
        index=df.index,
    )
    configured_service_prior = {
        service: float(service_cfg["amount"]["median"])
        for service, service_cfg in config["services"].items()
    }
    service_prior = df["service_category"].map(configured_service_prior).astype(float)
    df["service_typical_amount"] = historical_service_median.fillna(service_prior)
    df["claim_to_service_median_ratio"] = (
        df["claim_amount"] / df["service_typical_amount"]
    )
    df["claim_to_customer_avg_ratio"] = (
        df["claim_amount"] / df["customer_avg_claim_amount_365d"]
    )
    df["claim_to_provider_avg_ratio"] = (
        df["claim_amount"] / df["provider_avg_claim_amount_90d"]
    )
    ratio_columns = [
        "claim_to_service_median_ratio",
        "claim_to_customer_avg_ratio",
        "claim_to_provider_avg_ratio",
    ]
    df[ratio_columns] = df[ratio_columns].replace([np.inf, -np.inf], np.nan)
    return df


def _strict_previous_days(frame: pd.DataFrame, keys: list[str]) -> pd.Series:
    columns = keys + ["claim_submission_timestamp"]
    unique = frame[columns].drop_duplicates().copy()
    unique["_days"] = (
        unique.groupby(keys, sort=False, dropna=False)["claim_submission_timestamp"]
        .diff()
        .dt.total_seconds()
        .div(86400)
    )
    lookup = unique.set_index(columns)["_days"]
    return pd.Series(
        lookup.reindex(pd.MultiIndex.from_frame(frame[columns])).to_numpy(),
        index=frame.index,
    )
