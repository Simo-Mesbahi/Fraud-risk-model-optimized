"""Shared, versioned contracts for the public synthetic-data demonstration."""

from pathlib import Path
import yaml

CONTRACT_VERSION = "1.1.0"
MAX_BATCH_SIZE = 10_000
MAX_UPLOAD_BYTES = 16 * 1024 * 1024
MAX_UPLOAD_COLUMNS = 96
MAX_STRING_LENGTH = 256
MAX_ADVANCED_JSON_CHARS = 128_000
RECENT_POLICY_CHANGE_DAYS = 90
_policy_path = Path(__file__).resolve().parents[2] / "configs/thresholds.yaml"
if _policy_path.exists():
    with _policy_path.open(encoding="utf-8") as _file:
        _policy = yaml.safe_load(_file)
else:
    _policy = {
        "score_bands": {"low": 0.05, "medium": 0.20, "high": 0.50},
        "review_capacity": 0.03,
    }
RISK_LOW_THRESHOLD = float(_policy["score_bands"]["low"])
RISK_MEDIUM_THRESHOLD = float(_policy["score_bands"]["medium"])
RISK_HIGH_THRESHOLD = float(_policy["score_bands"]["high"])
DEFAULT_REVIEW_FRACTION = float(_policy["review_capacity"])
if (
    not 0 < RISK_LOW_THRESHOLD < RISK_MEDIUM_THRESHOLD < RISK_HIGH_THRESHOLD <= 1
    or not 0 < DEFAULT_REVIEW_FRACTION <= 1
):
    raise ValueError("Invalid presentation score bands or review capacity.")
LEAKAGE_COLUMNS = frozenset(
    {
        "is_fraud",
        "latent_fraud_score",
        "synthetic_fraud_probability",
        "fraud_mechanism",
        "fraud_difficulty",
        "legitimate_anomaly",
        "legitimate_anomaly_type",
        "customer_behavior_segment",
        "provider_behavior_segment",
    }
)
