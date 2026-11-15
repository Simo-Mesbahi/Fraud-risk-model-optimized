import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    log_loss,
    roc_auc_score,
)

from health_fraud.evaluation.metrics import bootstrap_intervals, metric_summary
from health_fraud.evaluation.quality import distribution_shift, quality_profile
from health_fraud.features.preprocessing import make_preprocessor


@pytest.mark.parametrize("seed", [2, 17, 42])
def test_metrics_agree_with_independent_sklearn_reference_including_ties(seed):
    rng = np.random.default_rng(seed)
    labels = rng.binomial(1, 0.15, 500)
    scores = rng.choice(np.linspace(0, 1, 21), 500)
    result = metric_summary(labels, scores)
    assert result["average_precision"] == pytest.approx(
        average_precision_score(labels, scores)
    )
    assert result["roc_auc"] == pytest.approx(roc_auc_score(labels, scores))
    assert result["brier_score"] == pytest.approx(brier_score_loss(labels, scores))
    assert result["log_loss"] == pytest.approx(log_loss(labels, scores))


def test_capacity_ceil_and_amount_capture_are_not_classification_thresholds():
    result = metric_summary(
        [1, 0, 1, 0], [0.04, 0.03, 0.02, 0.01], [100, 50, 200, 10], fraction=0.3
    )
    assert result["reviewed"] == 2
    assert result["true_positives"] == 1
    assert result["recall_at_capacity"] == 0.5
    assert result["fraud_amount_capture"] == pytest.approx(1 / 3)


def test_absent_positive_population_does_not_invent_performance():
    result = metric_summary([0, 0], [0.1, 0.2])
    assert result["average_precision"] is None
    assert result["roc_auc"] is None
    assert result["recall_at_capacity"] is None


def test_fractional_labels_and_nonfinite_scores_are_rejected():
    with pytest.raises(ValueError):
        metric_summary([0, 0.5], [0.1, 0.2])
    with pytest.raises(ValueError):
        metric_summary([0, 1], [0.1, float("nan")])


def test_cluster_bootstrap_is_reproducible():
    kwargs = dict(
        labels=[0, 1, 0, 1],
        scores=[0.1, 0.8, 0.3, 0.7],
        groups=["A", "A", "B", "B"],
        iterations=10,
        seed=4,
    )
    assert bootstrap_intervals(**kwargs) == bootstrap_intervals(**kwargs)


def test_preprocessing_learns_only_from_training_and_handles_unknown_categories():
    train = pd.DataFrame(
        {"claim_amount": [10.0, 20.0, np.nan], "service_category": ["A", "A", None]}
    )
    future = pd.DataFrame(
        {"claim_amount": [1_000_000.0, np.nan], "service_category": ["NEVER_SEEN", "A"]}
    )
    processor = make_preprocessor(list(train), scale=False)
    processor.fit(train)
    before = (
        processor.named_steps["columns"]
        .named_transformers_["numeric"]
        .named_steps["impute"]
        .statistics_.copy()
    )
    transformed = processor.transform(future)
    after = (
        processor.named_steps["columns"]
        .named_transformers_["numeric"]
        .named_steps["impute"]
        .statistics_
    )
    assert np.array_equal(before, after)
    assert before[0] == 15
    assert transformed.shape[0] == 2


def test_quality_counts_invalid_values_without_counting_structural_missing_as_fraud():
    frame = pd.DataFrame(
        {
            "claim_id": ["A", "A"],
            "claim_amount": [10.0, -1.0],
            "days_since_policy_change": [np.nan, np.nan],
        }
    )
    profile = quality_profile(frame)
    assert profile["rules"]["duplicate_claim_ids"] == 1
    assert profile["rules"]["negative_claim_amount"] == 1
    assert profile["column_profile"][2]["missingness_context"].startswith(
        "May represent"
    )
    assert distribution_shift(pd.Series([1] * 30), pd.Series([1] * 30))["psi"] is None
