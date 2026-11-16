"""The generator is deterministic and entity events obey point-in-time rules."""

import numpy as np
import pandas as pd
import pytest
import yaml

from health_fraud.data.generate import generate_synthetic_data, load_config
from health_fraud.data.scenarios import quality_challenge, scenario_config
from health_fraud.evaluation.quality import quality_profile


@pytest.fixture(scope="module")
def longitudinal_bundle(tmp_path_factory):
    config = scenario_config(load_config("configs/data.yaml"), "expanded", 2000, 1729)
    config["quality"]["inject_invalid_records"] = False
    path = tmp_path_factory.mktemp("synthetic") / "config.yaml"
    path.write_text(yaml.safe_dump(config))
    return path, generate_synthetic_data(path)


def test_generation_is_reproducible_without_mutating_the_reference_config(
    longitudinal_bundle,
):
    path, first = longitudinal_bundle
    second = generate_synthetic_data(path)
    pd.testing.assert_frame_equal(first.claims, second.claims)
    assert load_config("configs/data.yaml")["simulation"]["target_claims"] == 100000


def test_policy_events_cannot_apply_before_their_effective_date(longitudinal_bundle):
    _, bundle = longitudinal_bundle
    frame = bundle.claims
    events = frame.policy_id.map(
        bundle.policies.set_index("policy_id").policy_change_date
    )
    submitted = pd.to_datetime(frame.claim_submission_timestamp)
    past = events.notna() & (events <= submitted)
    assert frame.loc[~past, "days_since_policy_change"].isna().all()
    assert not frame.loc[~past, "recent_policy_change"].any()
    assert np.allclose(
        frame.loc[past, "days_since_policy_change"],
        (submitted[past] - events[past]).dt.total_seconds() / 86400,
    )
    starts = frame.policy_id.map(
        bundle.policies.set_index("policy_id").policy_start_date
    )
    expected = ((submitted - starts).dt.days / 30.4375).clip(lower=1).astype(int)
    assert frame.policy_tenure_months.equals(expected)


def test_controlled_corruption_is_a_separate_quality_fixture(longitudinal_bundle):
    _, bundle = longitudinal_bundle
    original = bundle.claims.copy(deep=True)
    challenge = quality_challenge(original)
    report = quality_profile(challenge)
    assert report["rules"]["negative_claim_amount"] > 0
    assert report["rules"]["duplicate_claim_ids"] > 0
    assert report["rules"]["service_after_submission"] > 0
    pd.testing.assert_frame_equal(original, bundle.claims)
