"""Consistent synthetic entity events, resolved as of each claim's timestamp."""

from __future__ import annotations

import numpy as np
import pandas as pd


def enrich_longitudinal(customers, providers, policies, claims, config, rng):
    customers, providers, policies, claims = (
        frame.copy() for frame in (customers, providers, policies, claims)
    )
    start = pd.Timestamp(config["simulation"]["start_date"])
    end = pd.Timestamp(config["simulation"]["end_date"])
    span = max(1, (end - start).days)
    settings = config.get("longitudinal_context", {})
    probability = float(settings.get("policy_event_probability", 0.8))
    dates = start + pd.to_timedelta(rng.integers(0, span + 1, len(policies)), unit="D")
    has_event = rng.random(len(policies)) < probability
    policies["policy_change_date"] = (
        pd.Series(dates).where(has_event, pd.NaT).to_numpy()
    )
    levels = list(config["policy"]["coverage_limits"])
    policies["new_coverage_level"] = [
        levels[(levels.index(str(old)) + 1) % len(levels)]
        for old in policies.coverage_level
    ]

    # Birth/join dates are simulated entities, not inferred facts about real people.
    customers["birth_date"] = start - pd.to_timedelta(
        customers.customer_age * 365.2425 + rng.integers(0, 365, len(customers)),
        unit="D",
    )
    customers["customer_start_date"] = start - pd.to_timedelta(
        customers.customer_tenure_months * 30.4375, unit="D"
    )
    providers["provider_start_date"] = start - pd.to_timedelta(
        providers.provider_tenure_months * 30.4375, unit="D"
    )
    policy_lookup = policies.set_index("policy_id")
    customer_lookup = customers.set_index("customer_id")
    provider_lookup = providers.set_index("provider_id")
    submitted = pd.to_datetime(claims.claim_submission_timestamp)
    changed_at = pd.to_datetime(claims.policy_id.map(policy_lookup.policy_change_date))
    changed = changed_at.notna() & (changed_at <= submitted)
    previous = claims.policy_id.map(policy_lookup.coverage_level)
    updated = claims.policy_id.map(policy_lookup.new_coverage_level)
    claims["coverage_level"] = previous.where(~changed, updated)
    claims["policy_tenure_months"] = (
        (
            (
                submitted
                - pd.to_datetime(claims.policy_id.map(policy_lookup.policy_start_date))
            ).dt.days
            / 30.4375
        )
        .clip(lower=1)
        .astype(int)
    )
    claims["days_since_policy_change"] = (
        (submitted - changed_at).dt.total_seconds() / 86400
    ).where(changed, np.nan)
    claims["recent_policy_change"] = changed & claims.days_since_policy_change.le(
        int(config["policy"]["recent_change_window_days"])
    )
    claims["customer_age"] = (
        (
            submitted
            - pd.to_datetime(claims.customer_id.map(customer_lookup.birth_date))
        ).dt.days
        / 365.2425
    ).astype(int)
    claims["customer_tenure_months"] = (
        (
            (
                submitted
                - pd.to_datetime(
                    claims.customer_id.map(customer_lookup.customer_start_date)
                )
            ).dt.days
            / 30.4375
        )
        .clip(lower=1)
        .astype(int)
    )
    claims["provider_tenure_months"] = (
        (
            (
                submitted
                - pd.to_datetime(
                    claims.provider_id.map(provider_lookup.provider_start_date)
                )
            ).dt.days
            / 30.4375
        )
        .clip(lower=1)
        .astype(int)
    )
    limits = config["policy"]["coverage_limits"]
    claims["coverage_limit"] = [
        limits[level][service]
        for level, service in zip(claims.coverage_level, claims.service_category)
    ]
    claims["requested_reimbursement"] = np.minimum(
        claims.requested_reimbursement,
        np.minimum(claims.claim_amount, claims.coverage_limit),
    )
    claims["reimbursement_ratio"] = claims.requested_reimbursement / claims.claim_amount
    return customers, providers, policies, claims
