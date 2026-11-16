"""Auditable ranking metrics with deterministic ties and no UI/ML dependency."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _arrays(labels, scores):
    raw_labels = np.asarray(labels)
    if not np.isin(raw_labels, [0, 1]).all():
        raise ValueError("Labels must be binary.")
    y = raw_labels.astype(int)
    s = np.asarray(scores, dtype=float)
    if y.ndim != 1 or s.shape != y.shape or len(y) == 0:
        raise ValueError("Labels and scores must be non-empty aligned vectors.")
    if (
        not np.isin(y, [0, 1]).all()
        or not np.isfinite(s).all()
        or ((s < 0) | (s > 1)).any()
    ):
        raise ValueError("Expected binary labels and finite scores in [0, 1].")
    return y, s


def curves(labels, scores) -> dict[str, np.ndarray]:
    y, s = _arrays(labels, scores)
    order = np.argsort(-s, kind="mergesort")
    sorted_scores = s[order]
    ends = np.flatnonzero(np.r_[sorted_scores[1:] != sorted_scores[:-1], True])
    true = np.cumsum(y[order])[ends].astype(float)
    false = ends + 1 - true
    positives = int(y.sum())
    negatives = len(y) - positives
    return {
        "threshold": sorted_scores[ends],
        "precision": true / (ends + 1),
        "recall": true / positives if positives else np.zeros(len(ends)),
        "fpr": false / negatives if negatives else np.zeros(len(ends)),
    }


def metric_summary(labels, scores, amounts=None, fraction: float = 0.03) -> dict:
    y, s = _arrays(labels, scores)
    if not 0 < fraction <= 1:
        raise ValueError("Review capacity must lie in (0, 1].")
    money = np.ones(len(y)) if amounts is None else np.asarray(amounts, dtype=float)
    if money.shape != y.shape or not np.isfinite(money).all() or (money < 0).any():
        raise ValueError("Claim amounts must be aligned, finite and non-negative.")
    selected = np.argsort(-s, kind="mergesort")[
        : max(1, int(np.ceil(len(y) * fraction)))
    ]
    true = int(y[selected].sum())
    positives = int(y.sum())
    negatives = len(y) - positives
    ranks = pd.Series(s).rank(method="average").to_numpy()
    curve = curves(y, s)
    ap = (
        float(np.sum(np.diff(np.r_[0, curve["recall"]]) * curve["precision"]))
        if positives
        else None
    )
    auc = (
        float(
            (ranks[y == 1].sum() - positives * (positives + 1) / 2)
            / (positives * negatives)
        )
        if positives and negatives
        else None
    )
    clipped = np.clip(s, np.finfo(float).eps, 1 - np.finfo(float).eps)
    fraud_amount = float(money[y == 1].sum())
    prevalence = positives / len(y)
    return {
        "claims": len(y),
        "fraud_cases": positives,
        "prevalence": prevalence,
        "average_precision": ap,
        "roc_auc": auc,
        "brier_score": float(np.mean((s - y) ** 2)),
        "log_loss": float(
            -np.mean(y * np.log(clipped) + (1 - y) * np.log(1 - clipped))
        ),
        "review_fraction": fraction,
        "reviewed": len(selected),
        "true_positives": true,
        "false_positives": len(selected) - true,
        "precision_at_capacity": true / len(selected),
        "recall_at_capacity": true / positives if positives else None,
        "lift_at_capacity": (true / len(selected)) / prevalence if prevalence else None,
        "fraud_amount_capture": float(
            (money[selected] * y[selected]).sum() / fraud_amount
        )
        if fraud_amount
        else None,
    }


def capacity_curve(labels, scores, amounts=None, fractions=None) -> pd.DataFrame:
    fractions = fractions or [0.005, 0.01, 0.02, 0.03, 0.05, 0.075, 0.10, 0.15, 0.20]
    return pd.DataFrame([metric_summary(labels, scores, amounts, f) for f in fractions])


def calibration_table(labels, scores, bins: int = 10) -> pd.DataFrame:
    y, s = _arrays(labels, scores)
    frame = pd.DataFrame({"observed": y, "score": s})
    frame["bin"] = pd.cut(s, bins=np.linspace(0, 1, bins + 1), include_lowest=True)
    return (
        frame.groupby("bin", observed=True)
        .agg(
            claims=("observed", "size"),
            mean_score=("score", "mean"),
            observed_rate=("observed", "mean"),
        )
        .reset_index()
        .assign(bin=lambda x: x["bin"].astype(str))
    )


def bootstrap_intervals(
    labels, scores, amounts=None, groups=None, iterations=150, seed=42
) -> dict:
    """Resample customer clusters when provided; intervals remain simulation-specific."""
    y, s = _arrays(labels, scores)
    money = np.ones(len(y)) if amounts is None else np.asarray(amounts)
    rng = np.random.default_rng(seed)
    clusters = (
        [
            np.asarray(v)
            for v in pd.Series(np.arange(len(y)))
            .groupby(np.asarray(groups), dropna=False)
            .groups.values()
        ]
        if groups is not None
        else None
    )
    fields = [
        "average_precision",
        "roc_auc",
        "recall_at_capacity",
        "fraud_amount_capture",
    ]
    values = {key: [] for key in fields}
    for _ in range(iterations):
        index = (
            np.concatenate(
                [clusters[i] for i in rng.integers(0, len(clusters), len(clusters))]
            )
            if clusters
            else rng.integers(0, len(y), len(y))
        )
        result = metric_summary(y[index], s[index], money[index])
        for key in fields:
            if result[key] is not None:
                values[key].append(result[key])
    return {
        "method": "customer-cluster bootstrap" if clusters else "claim bootstrap",
        "iterations": iterations,
        "seed": seed,
        "intervals": {
            key: [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))]
            if v
            else None
            for key, v in values.items()
        },
    }
