"""Reproducible research selection, refit and temporal evaluation.

Selection uses validation AP, then recall at capacity and Brier score. Test
metrics never select a model. The API's published reference is not overwritten.
"""

from __future__ import annotations

import importlib.metadata
import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import yaml
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from xgboost import XGBClassifier

from health_fraud.config import LEAKAGE_COLUMNS
from health_fraud.data.scenarios import sha256
from health_fraud.evaluation.metrics import (
    bootstrap_intervals,
    calibration_table,
    capacity_curve,
    curves,
    metric_summary,
)
from health_fraud.features.preprocessing import make_preprocessor
from health_fraud.features.research import RESEARCH_FEATURES, build_research_features
from health_fraud.models.calibrate import apply_platt, fit_platt


def model_settings():
    path = Path(__file__).resolve().parents[3] / "configs/model.yaml"
    with path.open(encoding="utf-8") as file:
        return yaml.safe_load(file)


@dataclass(frozen=True)
class Experiment:
    name: str
    kind: str
    features: tuple[str, ...]
    imputation: str = "median"
    scale: bool = True


def estimator(kind, seed=42):
    if kind == "dummy":
        return DummyClassifier(strategy="prior")
    if kind == "logistic":
        return LogisticRegression(max_iter=1500, solver="lbfgs", random_state=seed)
    if kind == "forest":
        return RandomForestClassifier(
            n_estimators=150,
            max_depth=8,
            min_samples_leaf=5,
            n_jobs=1,
            random_state=seed,
        )
    if kind != "xgboost":
        raise ValueError("Unknown estimator.")
    return XGBClassifier(**model_settings()["xgboost"], random_state=seed)


def pipeline_for(spec: Experiment, seed=42):
    forbidden = LEAKAGE_COLUMNS | {
        "claim_id",
        "customer_id",
        "policy_id",
        "provider_id",
        "service_date",
        "claim_submission_date",
        "claim_submission_timestamp",
    }
    if forbidden.intersection(spec.features):
        raise ValueError("Leakage or identifiers in model feature set.")
    return Pipeline(
        [
            ("features", FunctionTransformer(build_research_features)),
            ("select", ColumnSelector(spec.features)),
            (
                "preprocess",
                make_preprocessor(
                    list(spec.features), imputation=spec.imputation, scale=spec.scale
                ),
            ),
            ("model", estimator(spec.kind, seed)),
        ]
    )


class ColumnSelector:
    """Pickle-safe explicit feature allowlist; input column additions cannot leak."""

    def __init__(self, columns):
        self.columns = columns

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X.loc[:, list(self.columns)].copy()

    def fit_transform(self, X, y=None):
        return self.fit(X, y).transform(X)

    def get_params(self, deep=True):
        return {"columns": self.columns}

    def set_params(self, **params):
        self.columns = params.get("columns", self.columns)
        return self


def temporal_split(frame: pd.DataFrame):
    settings = model_settings()["temporal"]
    train_end = pd.Timestamp(settings["train_end"]) + pd.Timedelta(days=1)
    validation_end = pd.Timestamp(settings["validation_end"]) + pd.Timedelta(days=1)
    reference_end = pd.Timestamp(settings["reference_test_end"]) + pd.Timedelta(days=1)
    if not train_end < validation_end < reference_end:
        raise ValueError("Temporal split boundaries must be strictly ordered.")
    dates = pd.to_datetime(frame.claim_submission_timestamp, errors="raise")
    masks = {
        "train": dates < train_end,
        "validation": (dates >= train_end) & (dates < validation_end),
        "test_reference": (dates >= validation_end) & (dates < reference_end),
        "test_future": dates >= reference_end,
    }
    result = {
        name: frame.loc[mask]
        .sort_values("claim_submission_timestamp", kind="mergesort")
        .copy()
        for name, mask in masks.items()
    }
    for name in ("train", "validation", "test_reference"):
        if len(result[name]) < 50 or result[name].is_fraud.nunique() != 2:
            raise ValueError(
                f"Insufficient labelled data in chronological {name} split."
            )
    if set(result["train"].claim_id) & set(result["validation"].claim_id):
        raise ValueError("Repeated claim IDs across splits.")
    return result


def experiment_specs(features):
    frozen = tuple(features)
    history_terms = (
        "_claims_",
        "_amount_30",
        "_amount_365",
        "_avg_",
        "days_since_customer",
        "days_since_same",
        "claim_to_",
        "intensity",
        "activity",
        "recent_claim_share",
        "recent_amount_share",
        "service_typical",
        "amount_above_service",
    )
    no_history = tuple(
        f for f in frozen if not any(term in f for term in history_terms)
    )
    return [
        Experiment("Dummy prior", "dummy", frozen),
        Experiment("Logistic regression", "logistic", frozen),
        Experiment("Random forest", "forest", frozen, scale=False),
        Experiment("XGBoost · reference features", "xgboost", frozen),
        Experiment("XGBoost · no scaling", "xgboost", frozen, scale=False),
        Experiment(
            "XGBoost · frequent imputation",
            "xgboost",
            frozen,
            imputation="most_frequent",
            scale=False,
        ),
        Experiment(
            "XGBoost · extended features",
            "xgboost",
            frozen + tuple(RESEARCH_FEATURES),
            scale=False,
        ),
        Experiment("XGBoost · history ablation", "xgboost", no_history, scale=False),
    ]


def _curve_records(labels, scores, max_points=180):
    data = curves(labels, scores)
    indices = np.unique(
        np.linspace(
            0, len(data["precision"]) - 1, min(max_points, len(data["precision"]))
        ).astype(int)
    )
    return [{key: float(values[i]) for key, values in data.items()} for i in indices]


def _metrics(frame, scores):
    return metric_summary(frame.is_fraud, scores, frame.claim_amount)


def run_research(
    input_path="data/interim/claims.parquet",
    output_dir="artifacts/research/reference",
    seed=42,
    quick=False,
):
    input_path, output = Path(input_path), Path(output_dir)
    reference_dir = Path(__file__).resolve().parents[3] / "artifacts/models"
    if output.resolve() == reference_dir or reference_dir in output.resolve().parents:
        raise ValueError(
            "Research must not overwrite frozen production model artifacts."
        )
    output.mkdir(parents=True, exist_ok=True)
    frame = pd.read_parquet(input_path)
    if frame.claim_id.duplicated().any():
        raise ValueError("Duplicate claims in research corpus.")
    splits = temporal_split(frame)
    train, validation = splits["train"], splits["validation"]
    root = Path(__file__).resolve().parents[3]
    contract = json.loads(
        (root / "artifacts/metadata/health_fraud_model_metadata.json").read_text()
    )
    specs = experiment_specs(contract["features"])
    if quick:
        specs = [specs[0], specs[1], specs[3]]
    records = []
    for spec in specs:
        model = pipeline_for(spec, seed)
        started = time.perf_counter()
        model.fit(train, train.is_fraud)
        fit_seconds = time.perf_counter() - started
        started = time.perf_counter()
        scores = model.predict_proba(validation)[:, 1]
        seconds = time.perf_counter() - started
        record = {
            "name": spec.name,
            "kind": spec.kind,
            "feature_count": len(spec.features),
            "imputation": spec.imputation,
            "scaling": spec.scale,
            "fit_seconds": fit_seconds,
            "validation_score_seconds": seconds,
            "validation_metrics": _metrics(validation, scores),
            "validation_curve": _curve_records(validation.is_fraud, scores),
        }
        records.append(record)
        print(
            f"{spec.name}: validation AP={record['validation_metrics']['average_precision']:.4f}",
            flush=True,
        )
    selected = max(
        records,
        key=lambda r: (
            r["validation_metrics"]["average_precision"],
            r["validation_metrics"]["recall_at_capacity"],
            -r["validation_metrics"]["brier_score"],
        ),
    )
    selected_spec = next(s for s in specs if s.name == selected["name"])
    learning = []
    for fraction in [0.4, 1.0] if quick else [0.1, 0.25, 0.5, 0.75, 1.0]:
        subset = train.iloc[: max(100, int(len(train) * fraction))]
        if subset.is_fraud.nunique() != 2:
            continue
        candidate = pipeline_for(selected_spec, seed)
        candidate.fit(subset, subset.is_fraud)
        learning.append(
            {
                "training_claims": len(subset),
                "training_period_end": str(subset.claim_submission_timestamp.max()),
                "training_ap": _metrics(subset, candidate.predict_proba(subset)[:, 1])[
                    "average_precision"
                ],
                "validation_ap": _metrics(
                    validation, candidate.predict_proba(validation)[:, 1]
                )["average_precision"],
            }
        )

    # Calibration is compared on validation, using April–June only to fit Platt.
    calibration_trial = {}
    if not quick:
        calibration_start = pd.Timestamp(
            model_settings()["temporal"]["calibration_development_end"]
        ) + pd.Timedelta(days=1)
        development = train.loc[
            pd.to_datetime(train.claim_submission_timestamp) < calibration_start
        ]
        calibration = train.loc[
            pd.to_datetime(train.claim_submission_timestamp) >= calibration_start
        ]
        if development.is_fraud.nunique() == 2 and calibration.is_fraud.nunique() == 2:
            base = pipeline_for(
                next(s for s in specs if s.name == "XGBoost · reference features"), seed
            )
            base.fit(development, development.is_fraud)
            calibrator = fit_platt(
                base.predict_proba(calibration)[:, 1], calibration.is_fraud
            )
            raw = base.predict_proba(validation)[:, 1]
            calibration_trial = {
                "development_rows": len(development),
                "calibration_rows": len(calibration),
                "evaluation": "chronological validation only",
                "raw": _metrics(validation, raw),
                "platt": _metrics(validation, apply_platt(calibrator, raw)),
                "deployed": False,
            }

    # Only after selection, refit on pre-2026 data and open the reference/future tests.
    final = pipeline_for(selected_spec, seed)
    pretest = pd.concat([train, validation]).sort_values(
        "claim_submission_timestamp", kind="mergesort"
    )
    final.fit(pretest, pretest.is_fraud)
    tests = {}
    predictions = []
    for name in ["test_reference", "test_future"]:
        test = splits[name]
        if test.empty:
            continue
        scores = final.predict_proba(test)[:, 1]
        tests[name] = {
            "metrics": _metrics(test, scores),
            "capacity_curve": capacity_curve(
                test.is_fraud, scores, test.claim_amount
            ).to_dict("records"),
            "calibration": calibration_table(test.is_fraud, scores).to_dict("records"),
            "curve": _curve_records(test.is_fraud, scores),
            "uncertainty": bootstrap_intervals(
                test.is_fraud,
                scores,
                test.claim_amount,
                groups=test.customer_id,
                iterations=40 if quick else 150,
                seed=seed,
            ),
        }
        predictions.append(
            pd.DataFrame(
                {"claim_id": test.claim_id, "fraud_risk_score": scores, "split": name}
            )
        )
    pd.concat(predictions).to_parquet(
        output / "candidate_predictions.parquet", index=False
    )
    artifact = output / "candidate_pipeline.joblib"
    joblib.dump(final, artifact, compress=3)
    transformed = final.named_steps["preprocess"].get_feature_names_out()
    fitted = final.named_steps["model"]
    importance = getattr(fitted, "feature_importances_", None)
    if importance is None and hasattr(fitted, "coef_"):
        importance = np.abs(fitted.coef_[0])
    importance_records = sorted(
        [
            {"feature": str(k), "importance": float(v)}
            for k, v in zip(transformed, importance)
        ]
        if importance is not None
        else [],
        key=lambda x: -x["importance"],
    )
    manifest_path = input_path.parent / "manifest.json"
    origin = (
        json.loads(manifest_path.read_text())
        if manifest_path.exists()
        else {"dataset_version": "published-reference-v1", "synthetic": True}
    )
    report = {
        "schema_version": "1.0.0",
        "dataset": origin,
        "input_sha256": sha256(input_path),
        "seed": seed,
        "quick": quick,
        "selection_rule": "Highest validation Average Precision, then recall at 3%, then lower Brier score; no test selection.",
        "split_counts": {k: len(v) for k, v in splits.items()},
        "experiments": records,
        "selected": selected["name"],
        "learning_curve": learning,
        "calibration_trial": calibration_trial,
        "test_results": tests,
        "candidate_features": list(selected_spec.features),
        "candidate_importance": importance_records[:30],
        "candidate_sha256": sha256(artifact),
        "candidate_deployed": False,
        "published_reference_model_unchanged": True,
        "source_revision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
        "environment": {
            p: importlib.metadata.version(p)
            for p in [
                "numpy",
                "pandas",
                "scikit-learn",
                "xgboost-cpu",
                "shap",
                "pyarrow",
            ]
        },
        "interpretation": [
            "Synthetic-world performance; not a real insurance guarantee.",
            "Reference 2026-H1 has been reported before; it is a regression benchmark, not a newly untouched dataset.",
            "2026-H2 is a later simulated holdout when available.",
            "Candidate research does not silently replace the live reference model.",
        ],
    }
    (output / "report.json").write_text(
        json.dumps(report, indent=2, allow_nan=False), encoding="utf-8"
    )
    return report
