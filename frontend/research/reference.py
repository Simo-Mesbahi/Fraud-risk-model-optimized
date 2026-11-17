"""Compact frozen-model figures, tied to the actual recorded evaluation cohort."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from frontend.research.charts import BLUE, AMBER, GREEN, show_chart
from frontend.utils.presentation import readable_label, present_table

ROOT = Path(__file__).resolve().parents[2] / "artifacts/metadata"


@st.cache_data(show_spinner=False)
def reference_evidence():
    path = ROOT / "demo_evidence.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    metadata = ROOT / "health_fraud_model_metadata.json"
    if hashlib.sha256(metadata.read_bytes()).hexdigest() != data.get("metadata_sha256"):
        return {}
    return data


def validation_chart(kind: str, review_fraction: float = .03) -> bool:
    evidence = reference_evidence()
    if not evidence:
        return False
    if kind == "capacity":
        data = pd.DataFrame(evidence["capacity"]).melt(id_vars="review_fraction",
            value_vars=["recall_at_capacity", "precision_at_capacity", "fraud_amount_capture"],
            var_name="Outcome", value_name="value").dropna()
        data["Outcome"] = data.Outcome.map(readable_label)
        chart = alt.Chart(data).mark_line(point=True).encode(
            x=alt.X("review_fraction:Q", title="Claims reviewed", axis=alt.Axis(format=".0%")),
            y=alt.Y("value:Q", title="Outcome", axis=alt.Axis(format=".0%")),
            color=alt.Color("Outcome:N", scale=alt.Scale(
                domain=["Fraud recall", "Review precision", "Fraud amount captured"], range=[BLUE, AMBER, GREEN])),
            tooltip=["Outcome:N", alt.Tooltip("review_fraction:Q", title="Capacity", format=".1%"),
                     alt.Tooltip("value:Q", title="Outcome", format=".1%")])
        rule = alt.Chart(pd.DataFrame({"capacity": [review_fraction]})).mark_rule(strokeDash=[5, 5], color="#7E8CA5").encode(x="capacity:Q")
        chart = chart + rule
    elif kind in {"precision_recall", "roc"}:
        data = pd.DataFrame(evidence[kind])
        x_title, y_title = ("Fraud recall", "Precision") if kind == "precision_recall" else ("False-positive rate", "True-positive rate")
        chart = alt.Chart(data).mark_line(color=BLUE).encode(
            x=alt.X("x:Q", title=x_title, axis=alt.Axis(format=".0%"), scale=alt.Scale(domain=[0, 1])),
            y=alt.Y("y:Q", title=y_title, axis=alt.Axis(format=".0%"), scale=alt.Scale(domain=[0, 1])),
            tooltip=[alt.Tooltip("x:Q", title=x_title, format=".1%"), alt.Tooltip("y:Q", title=y_title, format=".1%")])
    elif kind == "calibration":
        data = pd.DataFrame(evidence["calibration"]).dropna(subset=["mean_score", "observed_rate"])
        chart = alt.Chart(data).mark_line(point=True, color=BLUE).encode(
            x=alt.X("mean_score:Q", title="Mean model risk", scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format=".0%")),
            y=alt.Y("observed_rate:Q", title="Observed synthetic fraud", scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format=".0%")),
            tooltip=["claims:Q", alt.Tooltip("mean_score:Q", format=".1%"), alt.Tooltip("observed_rate:Q", format=".1%")])
        baseline = alt.Chart(pd.DataFrame({"x": [0, 1], "y": [0, 1]})).mark_line(color="#7E8CA5", strokeDash=[4, 4]).encode(x="x:Q", y="y:Q")
        chart = chart + baseline
    elif kind == "confusion":
        data = pd.DataFrame(evidence["confusion"])
        base = alt.Chart(data).encode(x=alt.X("selection:N", title=None, axis=alt.Axis(labelAngle=0)),
                                     y=alt.Y("actual:N", title=None))
        chart = base.mark_rect(cornerRadius=6).encode(color=alt.Color("claims:Q", scale=alt.Scale(range=["#142239", BLUE]), legend=None)) + base.mark_text(color="#F8FAFC", fontSize=18).encode(text=alt.Text("claims:Q", format=","))
    else:
        return False
    show_chart(chart, height=300)
    st.caption(f"Frozen reference v{evidence['model_version']} · {evidence['claims']:,} held-out claims · January–June 2026. Curve displays use up to 250 points; metrics use every claim.")
    with st.expander("View chart data"):
        present_table(data, width="stretch", hide_index=True)
    return True
