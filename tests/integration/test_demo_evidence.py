"""The polished charts must describe the actual frozen reference evaluation."""
import json
from pathlib import Path

import numpy as np

from scripts.build_demo_evidence import build
import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[2]


def test_reference_figures_are_reproducible_and_match_frozen_metrics():
    actual = build()
    recorded = json.loads((ROOT / "artifacts/metadata/demo_evidence.json").read_text())
    assert actual == recorded
    assert actual["claims"] == 14176 and actual["frauds"] == 409
    assert sum(cell["claims"] for cell in actual["confusion"]) == actual["claims"]
    assert np.isclose(actual["prevalence"], 409 / 14176)


def test_every_scored_curve_has_bounded_values_and_meaningful_denominators():
    data = build()
    for name in ["precision_recall", "roc"]:
        assert 2 <= len(data[name]) <= 250
        assert all(0 <= point["x"] <= 1 and 0 <= point["y"] <= 1 for point in data[name])
    assert sum(row["claims"] for row in data["calibration"]) == data["claims"]


@pytest.mark.parametrize("kind", ["capacity", "precision_recall", "roc", "calibration", "confusion"])
def test_interactive_reference_figures_render_without_losing_their_context(kind):
    ui = AppTest.from_string(
        "from frontend.research.reference import validation_chart\n"
        f"validation_chart({kind!r})"
    ).run(timeout=30)
    assert not ui.exception
    assert any("14,176 held-out claims" in caption.value for caption in ui.caption)
