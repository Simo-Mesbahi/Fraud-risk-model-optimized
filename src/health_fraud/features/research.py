"""Candidate-only features. The frozen 57-feature inference contract stays explicit."""

import numpy as np
import pandas as pd

from health_fraud.features.build import build_model_features

RESEARCH_FEATURES = [
    "log_claim_amount",
    "amount_per_unit",
    "log_submission_delay",
    "provider_customer_activity_ratio",
]


def build_research_features(claims: pd.DataFrame) -> pd.DataFrame:
    result = build_model_features(claims)
    result["log_claim_amount"] = np.log1p(result.claim_amount.clip(lower=0))
    result["amount_per_unit"] = result.claim_amount / result.service_units.replace(
        0, np.nan
    )
    result["log_submission_delay"] = np.log1p(
        result.days_service_to_submission.clip(lower=0)
    )
    result["provider_customer_activity_ratio"] = (result.provider_claims_30d + 1) / (
        result.customer_claims_30d + 1
    )
    return result
