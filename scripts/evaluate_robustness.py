"""Evaluate frozen candidates in independent simulated worlds without refitting."""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

from api.app.dependencies import get_fraud_scorer
from health_fraud.data.scenarios import materialize_scenario
from health_fraud.evaluation.metrics import metric_summary

ROOT = Path(__file__).resolve().parents[1]


def main():
    candidates = {
        key: joblib.load(ROOT / f"artifacts/research/{key}/candidate_pipeline.joblib")
        for key in ["reference", "expanded"]
    }
    records = {key: [] for key in candidates}
    published = get_fraud_scorer()
    for scenario in ["hard_cases", "population_shift", "missing_evidence"]:
        for seed in [2718, 31415]:
            output = ROOT / f"data/research/{scenario}-{seed}"
            manifest = materialize_scenario(ROOT / "configs/data.yaml", output, name=scenario, rows=20000, seed=seed)
            frame = pd.read_parquet(output / "claims.parquet")
            frame = frame.loc[pd.to_datetime(frame.claim_submission_timestamp) >= "2026-01-01"].copy()
            published_scores = published.score(frame).fraud_risk_score.to_numpy()
            for key, model in candidates.items():
                scores = model.predict_proba(frame)[:, 1]
                result = metric_summary(frame.is_fraud, scores, frame.claim_amount)
                reference = metric_summary(frame.is_fraud, published_scores, frame.claim_amount)
                records[key].append({
                    "scenario": scenario, "seed": seed,
                    "claims_generated": manifest["accepted_claims"],
                    "claims_evaluated": len(frame),
                    "fraud_prevalence": result["prevalence"],
                    "candidate_AP": result["average_precision"],
                    "candidate_recall_at_3pct": result["recall_at_capacity"],
                    "published_model_AP": reference["average_precision"],
                    "published_recall_at_3pct": reference["recall_at_capacity"],
                    "data_sha256": manifest["files_sha256"]["claims"],
                    "refitted_on_scenario": False,
                })
            print(f"Evaluated {scenario}, seed {seed}, {len(frame)} held-out claims", flush=True)
    for key, results in records.items():
        path = ROOT / f"artifacts/research/{key}/report.json"
        report = json.loads(path.read_text())
        report["robustness_scenarios"] = results
        report["robustness_limitations"] = [
            "Independent synthetic worlds, with 20,000 requested claims each; no model refitting or selection.",
            "Evaluation covers 2026 only. World size also changes historical density; differences are scenario sensitivity, not causal estimates.",
            "These tests do not establish performance on real insurance data.",
        ]
        path.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")


if __name__ == "__main__":
    main()
