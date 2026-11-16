"""Build reproducible public data assets; large binaries live in a versioned release."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

import pandas as pd

from health_fraud.data.scenarios import materialize_scenario, quality_challenge, sha256
from health_fraud.evaluation.quality import quality_profile
from health_fraud.models.train import Experiment, pipeline_for, temporal_split

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts/research"


def reconstruct_candidate(data: Path, report: dict, output: Path):
    frame = pd.read_parquet(data)
    parts = temporal_split(frame)
    record = next(e for e in report["experiments"] if e["name"] == report["selected"])
    specification = Experiment(
        record["name"],
        record["kind"],
        tuple(report["candidate_features"]),
        record["imputation"],
        record["scaling"],
    )
    model = pipeline_for(specification, report["seed"])
    train = pd.concat([parts["train"], parts["validation"]]).sort_values(
        "claim_submission_timestamp", kind="mergesort"
    )
    model.fit(train, train.is_fraud)
    predictions = []
    for name in ["test_reference", "test_future"]:
        test = parts[name]
        if not test.empty:
            predictions.append(
                pd.DataFrame(
                    {
                        "claim_id": test.claim_id,
                        "fraud_risk_score": model.predict_proba(test)[:, 1],
                        "split": name,
                    }
                )
            )
    pd.concat(predictions).to_parquet(output, index=False)


def build(rebuild=False):
    expanded = ROOT / "data/research/expanded"
    if not (expanded / "claims.parquet").exists():
        materialize_scenario(
            ROOT / "configs/data.yaml", expanded, rows=150000, seed=1729
        )
    paths = {
        "reference": ROOT / "data/interim/claims.parquet",
        "expanded": expanded / "claims.parquet",
    }
    for key, path in paths.items():
        directory = ARTIFACTS / key
        directory.mkdir(parents=True, exist_ok=True)
        report = json.loads((directory / "report.json").read_text())
        if sha256(path) != report["input_sha256"]:
            raise ValueError(
                f"{key}: corpus differs from the recorded experiment. Re-run and review the scientific experiment before publishing."
            )
        predictions = directory / "candidate_predictions.parquet"
        if rebuild or not predictions.exists():
            reconstruct_candidate(path, report, predictions)
    shutil.copyfile(
        expanded / "claims.parquet", ARTIFACTS / "expanded/explorer.parquet"
    )
    if not (ARTIFACTS / "expanded/dataset.json").exists():
        shutil.copyfile(expanded / "manifest.json", ARTIFACTS / "expanded/dataset.json")
    if not (ARTIFACTS / "expanded/quality.json").exists():
        shutil.copyfile(expanded / "quality.json", ARTIFACTS / "expanded/quality.json")
    reference = pd.read_parquet(paths["reference"])
    quality = {
        "raw": quality_profile(pd.read_parquet(ROOT / "data/synthetic/claims.parquet")),
        "clean": quality_profile(reference),
        "rejected": quality_profile(
            pd.read_parquet(ROOT / "data/interim/claims_rejected.parquet")
        ),
        "challenge": quality_profile(quality_challenge(reference)),
    }
    (ARTIFACTS / "reference/quality.json").write_text(
        json.dumps(quality, indent=2), encoding="utf-8"
    )
    scores_path = ARTIFACTS / "expanded/reference_scores.parquet"
    if rebuild or not scores_path.exists():
        from api.app.dependencies import get_fraud_scorer

        scorer = get_fraud_scorer()
        frame = pd.read_parquet(paths["expanded"])
        scores = pd.concat(
            [
                scorer.score(frame.iloc[i : i + 5000])
                for i in range(0, len(frame), 5000)
            ],
            ignore_index=True,
        )
        scores.to_parquet(scores_path, index=False)
    names = [
        ("expanded/explorer.parquet", "expanded-claims.parquet"),
        ("expanded/reference_scores.parquet", "expanded-reference-scores.parquet"),
        (
            "expanded/candidate_predictions.parquet",
            "expanded-candidate-predictions.parquet",
        ),
        (
            "reference/candidate_predictions.parquet",
            "reference-candidate-predictions.parquet",
        ),
    ]
    entries = [
        {
            "path": "artifacts/research/" + path,
            "name": name,
            "sha256": sha256(ARTIFACTS / path),
            "bytes": (ARTIFACTS / path).stat().st_size,
        }
        for path, name in names
    ]
    identity = hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()[
        :12
    ]
    manifest = {
        "schema_version": "1.0.0",
        "repository": "Simo-Mesbahi/Fraud-risk-model-optimized",
        "release_tag": "fraud-research-v4-" + identity,
        "synthetic": True,
        "assets": entries,
    }
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument(
        "--write-manifest",
        action="store_true",
        help="Use only after reviewing new experiment results; never overwrites an existing release.",
    )
    args = parser.parse_args()
    manifest = build(args.rebuild)
    path = ROOT / "configs/research-assets.json"
    if args.write_manifest:
        path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    else:
        expected = json.loads(path.read_text())
        if manifest != expected:
            raise RuntimeError("Rebuilt data assets differ from the reviewed manifest.")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
