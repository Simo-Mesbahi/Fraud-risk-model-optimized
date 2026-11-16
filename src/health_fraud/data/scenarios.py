"""Versioned research worlds; the published reference corpus is never overwritten."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from health_fraud.data.clean import clean_claims
from health_fraud.data.generate import generate_synthetic_data, load_config
from health_fraud.evaluation.quality import quality_profile

SCENARIOS = ("expanded", "hard_cases", "population_shift", "missing_evidence")


def scenario_config(base: dict, name: str, rows: int, seed: int) -> dict:
    if name not in SCENARIOS or not 100 <= rows <= 1_000_000:
        raise ValueError("Unknown scenario or corpus size outside [100, 1,000,000].")
    config = copy.deepcopy(base)
    config["project"]["random_seed"] = seed
    config["simulation"].update(
        target_claims=rows,
        n_customers=min(25000, max(100, rows // 6)),
        n_providers=min(1500, max(30, rows // 100)),
        end_date="2026-10-31",
    )
    config["longitudinal_context"] = {"enabled": True, "policy_event_probability": 0.8}
    if name == "hard_cases":
        config["fraud"]["difficulty_mix"] = {"easy": 0.10, "medium": 0.35, "hard": 0.55}
        config["legitimate_anomalies"]["prevalence"] = 0.08
    elif name == "population_shift":
        config["entities"]["customers"]["age"].update(mean=54, std=19)
        config["entities"]["customers"]["behavior_segments"] = {
            "low_usage": 0.25,
            "regular": 0.43,
            "high_usage": 0.26,
            "atypical": 0.06,
        }
        config["entities"]["providers"]["regions"] = {
            "north": 0.10,
            "south": 0.15,
            "east": 0.35,
            "west": 0.15,
            "central": 0.25,
        }
        for service in config["services"].values():
            service["amount"]["sigma"] *= 1.15
    elif name == "missing_evidence":
        for field in (
            "provider_id_probability",
            "prescription_missing_probability",
            "document_count_missing_probability",
        ):
            config["missingness"][field] = min(0.25, config["missingness"][field] * 3)
    config["research_scenario"] = {"name": name, "version": "4.0.0", "synthetic": True}
    return config


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def quality_challenge(frame: pd.DataFrame, seed=42) -> pd.DataFrame:
    """A small deliberately corrupted fixture; never consumed by model fitting."""
    result = frame.head(600).copy().reset_index(drop=True)
    if len(result) < 10:
        return result
    rng = np.random.default_rng(seed)
    positions = rng.permutation(len(result))
    result.loc[positions[:20], "claim_amount"] = -10.0
    result.loc[positions[20:40], "service_units"] = 0
    result.loc[positions[40:60], "document_count"] = np.nan
    result.loc[positions[60:80], "service_date"] = pd.to_datetime(
        result.loc[positions[60:80], "claim_submission_timestamp"]
    ).to_numpy() + pd.Timedelta(days=7)
    result.loc[positions[80:90], "claim_id"] = "CONTROLLED_DUPLICATE"
    return result


def materialize_scenario(
    base_config: str | Path,
    output: str | Path,
    *,
    name="expanded",
    rows=150000,
    seed=1729,
) -> dict:
    output = Path(output).resolve()
    root = Path(__file__).resolve().parents[3]
    protected = [
        (root / "data/interim").resolve(),
        (root / "data/synthetic").resolve(),
        (root / "artifacts/models").resolve(),
    ]
    if any(output == path or path in output.parents for path in protected):
        raise ValueError(
            "Research output must not overwrite reference data or model directories."
        )
    output.mkdir(parents=True, exist_ok=True)
    config = scenario_config(load_config(base_config), name, rows, seed)
    resolved = output / "config.resolved.yaml"
    resolved.write_text(yaml.safe_dump(config, sort_keys=True), encoding="utf-8")
    bundle = generate_synthetic_data(resolved)
    clean, rejected = clean_claims(bundle.claims)
    tables = {
        "customers": bundle.customers,
        "providers": bundle.providers,
        "policies": bundle.policies,
        "claims": clean,
        "claims_rejected": rejected,
        "quality_challenge": quality_challenge(clean, seed),
    }
    hashes = {}
    for key, table in tables.items():
        path = output / f"{key}.parquet"
        table.to_parquet(path, index=False)
        hashes[key] = sha256(path)
    manifest = {
        "dataset_version": "4.0.0",
        "scenario": name,
        "seed": seed,
        "synthetic": True,
        "requested_claims": rows,
        "accepted_claims": len(clean),
        "rejected_claims": len(rejected),
        "fraud_prevalence": float(clean.is_fraud.mean()),
        "config_sha256": sha256(resolved),
        "files_sha256": hashes,
        "source_revision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
        "reference_data_unchanged": True,
        "quality_challenge_used_for_training": False,
        "limitations": [
            "Programmatic simulation; not real insurance performance.",
            "One simulated policy event per affected policy; unobserved real-world mechanisms remain outside this model.",
        ],
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    quality = {
        "raw": quality_profile(bundle.claims),
        "clean": quality_profile(clean),
        "rejected": quality_profile(rejected),
        "challenge": quality_profile(tables["quality_challenge"]),
    }
    (output / "quality.json").write_text(
        json.dumps(quality, indent=2), encoding="utf-8"
    )
    return manifest
