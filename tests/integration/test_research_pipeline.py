import json

import joblib
import numpy as np
import pytest
import yaml

from health_fraud.data.clean import clean_claims
from health_fraud.data.generate import generate_synthetic_data, load_config
from health_fraud.data.scenarios import scenario_config
from health_fraud.models.train import Experiment, pipeline_for, run_research


def test_research_pipeline_is_executable_and_does_not_replace_reference(tmp_path):
    config = scenario_config(load_config("configs/data.yaml"), "expanded", 2500, 1729)
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(config))
    bundle = generate_synthetic_data(path)
    clean, _ = clean_claims(bundle.claims)
    data = tmp_path / "claims.parquet"
    clean.to_parquet(data, index=False)
    report = run_research(data, tmp_path / "artifacts", seed=42, quick=True)
    assert report["candidate_deployed"] is False
    assert report["published_reference_model_unchanged"] is True
    assert len(report["experiments"]) == 3
    assert report["split_counts"]["test_future"] > 0
    assert set(report["test_results"]) == {"test_reference", "test_future"}
    model = joblib.load(tmp_path / "artifacts/candidate_pipeline.joblib")
    scores = model.predict_proba(clean.head(10))[:, 1]
    assert np.isfinite(scores).all()
    assert ((scores >= 0) & (scores <= 1)).all()
    assert json.loads((tmp_path / "artifacts/report.json").read_text())[
        "candidate_sha256"
    ]


def test_target_or_entity_identifiers_cannot_be_selected_as_features():
    for forbidden in ["is_fraud", "customer_id", "synthetic_fraud_probability"]:
        with pytest.raises(ValueError, match="Leakage"):
            pipeline_for(Experiment("invalid", "xgboost", ("claim_amount", forbidden)))
