"""Render all eight real analytical views without depending on a live API."""

import pytest
from streamlit.testing.v1 import AppTest


@pytest.mark.parametrize(
    "workspace",
    [
        "Exploration",
        "Data quality",
        "Time & evaluation splits",
        "Fraud patterns",
        "Model experiments",
        "Investigation capacity",
        "Explainability & errors",
        "Robustness & drift",
    ],
)
def test_science_workspaces_render_real_reference_artifacts(workspace):
    app = AppTest.from_string("from frontend.views.data_science import render\nrender(None)").run(
        timeout=30
    )
    assert not app.exception, [e.message for e in app.exception]
    app.selectbox(key="science_workspace").select(workspace).run(timeout=30)
    assert not app.exception, [e.message for e in app.exception]
    assert app.metric


def test_science_filters_handle_empty_cohorts_without_a_crash():
    app = AppTest.from_string("from frontend.views.data_science import render\nrender(None)").run(
        timeout=30
    )
    app.multiselect[0].select("dental").run(timeout=30)
    assert not app.exception
    assert app.metric[0].value != "0"


@pytest.mark.parametrize("workspace", ["Exploration", "Data quality", "Time & evaluation splits", "Fraud patterns", "Model experiments", "Investigation capacity", "Explainability & errors", "Robustness & drift"])
def test_expanded_corpus_and_candidate_are_rendered_from_real_artifacts(workspace):
    app = AppTest.from_string("from frontend.views.data_science import render\nrender(None)").run(timeout=30)
    corpus = next(option for option in app.selectbox(key="science_corpus").options if option.startswith("Expanded"))
    app.selectbox(key="science_corpus").select(corpus).run(timeout=30)
    app.selectbox(key="science_workspace").select(workspace).run(timeout=30)
    if workspace in {"Investigation capacity", "Explainability & errors", "Robustness & drift"}:
        app.radio(key="science_model").set_value("Research candidate · held-out scores").run(timeout=30)
    assert not app.exception, [e.message for e in app.exception]
    assert app.metric
