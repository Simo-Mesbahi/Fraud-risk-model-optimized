"""Immutable public-corpus loading and strict model/dataset provenance checks."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "artifacts/research"


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


@dataclass(frozen=True)
class Corpus:
    frame: pd.DataFrame
    report: dict
    quality: dict
    dataset_id: str
    name: str


def available_corpora():
    result = {}
    for key, label in [
        ("reference", "Published reference"),
        ("expanded", "Expanded longitudinal research"),
    ]:
        if key == "expanded" and not (RESEARCH / "expanded/explorer.parquet").exists():
            continue
        report = _json(RESEARCH / key / "report.json")
        count = sum(report.get("split_counts", {}).values())
        result[f"{label} · {count:,} claims" if count else label] = key
    return result


@st.cache_resource(max_entries=2, show_spinner=False)
def load_corpus(key: str) -> Corpus:
    """Only bundled synthetic data are cached globally. Consumers never mutate it."""
    if key not in {"reference", "expanded"}:
        raise ValueError("Unknown corpus.")
    path = (
        ROOT / "data/interim/claims.parquet"
        if key == "reference"
        else RESEARCH / "expanded/explorer.parquet"
    )
    report = _json(RESEARCH / key / "report.json")
    digest = file_digest(path)
    if report and report.get("input_sha256") != digest:
        raise ValueError("Dataset and experiment report fingerprints do not match.")
    frame = pd.read_parquet(path)
    if frame.claim_id.duplicated().any():
        raise ValueError("Ambiguous claim IDs in analytical corpus.")
    reference_path = (
        ROOT / "artifacts/predictions/claim_scores.parquet"
        if key == "reference"
        else RESEARCH / key / "reference_scores.parquet"
    )
    if reference_path.exists():
        scores = pd.read_parquet(reference_path)[
            ["claim_id", "fraud_risk_score"]
        ].rename(columns={"fraud_risk_score": "reference_score"})
        frame = frame.merge(scores, on="claim_id", how="left", validate="one_to_one")
        if frame.reference_score.isna().any():
            raise ValueError("Incomplete reference scoring artifact.")
    candidate_path = RESEARCH / key / "candidate_predictions.parquet"
    if candidate_path.exists() and report:
        candidate = pd.read_parquet(candidate_path)[
            ["claim_id", "fraud_risk_score"]
        ].rename(columns={"fraud_risk_score": "candidate_score"})
        frame = frame.merge(candidate, on="claim_id", how="left", validate="one_to_one")
    for column in ["reference_score", "candidate_score"]:
        if column not in frame:
            frame[column] = np.nan
        values = frame[column].dropna()
        if not np.isfinite(values).all() or not values.between(0, 1).all():
            raise ValueError("Invalid analytical score artifact.")
    frame["claim_submission_timestamp"] = pd.to_datetime(
        frame.claim_submission_timestamp
    )
    for column in [
        "service_category",
        "coverage_level",
        "provider_type",
        "provider_region",
        "submission_channel",
        "fraud_mechanism",
        "fraud_difficulty",
        "customer_behavior_segment",
        "provider_behavior_segment",
    ]:
        if column in frame:
            frame[column] = frame[column].astype("category")
    return Corpus(
        frame=frame,
        report=report,
        quality=_json(RESEARCH / key / "quality.json"),
        dataset_id=digest[:12],
        name=key,
    )


def evaluation_frame(frame: pd.DataFrame, score: str) -> pd.DataFrame:
    """Never report in-sample scores as out-of-time model performance."""
    return frame.loc[
        (frame.claim_submission_timestamp >= "2026-01-01") & frame[score].notna()
    ].copy()
