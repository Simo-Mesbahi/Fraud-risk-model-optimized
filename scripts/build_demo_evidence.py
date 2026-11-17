"""Persist compact, exact reference-cohort evidence for the public dashboard."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score, precision_recall_curve, roc_curve

from health_fraud.evaluation.metrics import calibration_table, capacity_curve, metric_summary

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def records(frame):
    return frame.astype(object).where(frame.notna(), None).to_dict(orient="records")


def sampled(x, y):
    indices = np.unique(np.linspace(0, len(x) - 1, min(250, len(x)), dtype=int))
    return [{"x": float(x[i]), "y": float(y[i])} for i in indices]


def build():
    metadata_path = ROOT / "artifacts/metadata/health_fraud_model_metadata.json"
    claims_path = ROOT / "data/interim/claims.parquet"
    scores_path = ROOT / "artifacts/predictions/claim_scores.parquet"
    metadata = json.loads(metadata_path.read_text())
    claims = pd.read_parquet(claims_path, columns=["claim_id", "claim_submission_timestamp", "is_fraud", "claim_amount"])
    dates = pd.to_datetime(claims.claim_submission_timestamp)
    cohort = claims.loc[dates.between(metadata["test_period"]["start"], metadata["test_period"]["end"])].copy()
    scores = pd.read_parquet(scores_path, columns=["claim_id", "fraud_risk_score"])
    cohort = cohort.merge(scores, on="claim_id", how="left", validate="one_to_one")
    if cohort.fraud_risk_score.isna().any():
        raise ValueError("Incomplete frozen scoring evidence.")
    y, p = cohort.is_fraud.to_numpy(), cohort.fraud_risk_score.to_numpy()
    metrics = metadata["final_test_metrics"]
    for key, value in [("average_precision", average_precision_score(y, p)), ("roc_auc", roc_auc_score(y, p))]:
        if not np.isclose(value, metrics[key], rtol=0, atol=1e-10):
            raise ValueError("Reference cohort differs from frozen " + key)
    precision, recall, _ = precision_recall_curve(y, p)
    fpr, tpr, _ = roc_curve(y, p)
    review_fraction = float(metadata["review_policy"]["fraction"])
    summary = metric_summary(y, p, cohort.claim_amount, review_fraction)
    selected = np.zeros(len(cohort), dtype=bool)
    selected[np.argsort(-p, kind="stable")[:int(np.ceil(len(p) * review_fraction))]] = True
    matrix = [{"actual": actual, "selection": selection, "claims": int(((y == label) & (selected == chosen)).sum())}
              for actual, label in [("Synthetic fraud", 1), ("Legitimate label", 0)]
              for selection, chosen in [("Selected for review", True), ("Not selected", False)]]
    return {
        "model_version": metadata["model_version"], "claims": len(cohort), "frauds": int(y.sum()),
        "prevalence": float(y.mean()), "period": metadata["test_period"],
        "review_fraction": review_fraction, "summary": summary,
        "metadata_sha256": digest(metadata_path), "claims_sha256": digest(claims_path),
        "scores_sha256": digest(scores_path),
        "capacity": records(capacity_curve(y, p, cohort.claim_amount)),
        "calibration": records(calibration_table(y, p)),
        "precision_recall": sampled(recall, precision), "roc": sampled(fpr, tpr),
        "confusion": matrix,
    }


if __name__ == "__main__":
    output = ROOT / "artifacts/metadata/demo_evidence.json"
    output.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n")
    print(f"Verified reference evidence saved: {output.name}")
