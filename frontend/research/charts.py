"""Small accessible charts; compute aggregates before sending data to the browser."""

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

BLUE = "#6CA6FF"
AMBER = "#FFD166"
GREEN = "#61E7A6"
PURPLE = "#B79BFF"


def show_chart(chart, *, height=300):
    chart = (
        chart.properties(height=height)
        .configure_view(strokeOpacity=0)
        .configure_axis(
            labelColor="#ABB8CE",
            titleColor="#E5EDF9",
            gridColor="#243047",
            labelFontSize=12,
            titleFontSize=12,
        )
        .configure_legend(labelColor="#C5D1E5", titleColor="#E5EDF9", labelLimit=300)
    )
    st.altair_chart(chart, width="stretch")


def histogram(frame, field="claim_amount", by_label=False):
    records = []
    positive = pd.to_numeric(frame[field], errors="coerce").dropna()
    positive = positive[positive > 0]
    if positive.empty:
        return
    low, high = float(positive.min()), float(positive.max())
    bins = np.geomspace(max(low, 0.001), max(high * 1.001, low * 1.01), 35)
    groups = (
        [("All claims", frame)]
        if not by_label
        else [
            ("Legitimate label", frame.loc[frame.is_fraud == 0]),
            ("Fraud label", frame.loc[frame.is_fraud == 1]),
        ]
    )
    for label, group in groups:
        values = pd.to_numeric(group[field], errors="coerce").dropna()
        counts, _ = np.histogram(values, bins)
        records.extend(
            {
                "from": float(bins[i]),
                "to": float(bins[i + 1]),
                "claims": int(n),
                "share": float(n / max(1, len(values))),
                "label": label,
            }
            for i, n in enumerate(counts)
        )
    data = pd.DataFrame(records)
    chart = (
        alt.Chart(
            data,
            description=f"Distribution of {field}; logarithmic monetary axis and explicit bin counts.",
        )
        .mark_bar(opacity=0.6)
        .encode(
            x=alt.X(
                "from:Q",
                title=f"{field.replace('_', ' ').title()} (€) · log scale",
                scale=alt.Scale(type="log"),
            ),
            x2="to:Q",
            y=alt.Y("share:Q", title="Within-group share", axis=alt.Axis(format=".0%")),
            color=alt.Color(
                "label:N", scale=alt.Scale(range=[BLUE, AMBER]), title="Synthetic label"
            ),
            tooltip=[
                alt.Tooltip("from:Q", format=",.2f"),
                alt.Tooltip("to:Q", format=",.2f"),
                "claims:Q",
                alt.Tooltip("share:Q", format=".1%"),
                "label:N",
            ],
        )
    )
    show_chart(chart)


def bar(frame, x, y, *, color=BLUE, percentage=False, title=None):
    if frame.empty:
        return
    tooltip = [
        alt.Tooltip(x + ":N", title=x.replace("_", " ").title()),
        alt.Tooltip(y + ":Q", format=".2%" if percentage else ",.2f"),
    ]
    show_chart(
        alt.Chart(frame, description=title or f"{y} by {x}")
        .mark_bar(color=color, cornerRadiusEnd=4)
        .encode(
            y=alt.Y(x + ":N", sort="-x", title=None),
            x=alt.X(
                y + ":Q",
                title=title or y.replace("_", " ").title(),
                axis=alt.Axis(format=".0%") if percentage else alt.Axis(),
            ),
            tooltip=tooltip,
        )
    )


def fraction(value):
    return "—" if value is None or pd.isna(value) else f"{value:.1%}"


def number(value):
    return "—" if value is None or pd.isna(value) else f"{value:,.0f}"


def evidence_table(frame, label="View chart data"):
    with st.expander(label):
        st.dataframe(frame, width="stretch", hide_index=True)
