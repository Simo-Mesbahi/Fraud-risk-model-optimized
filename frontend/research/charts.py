"""Small accessible charts; compute aggregates before sending data to the browser."""

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from frontend.utils.presentation import present_table, readable_label, wrapped_label

BLUE = "#3977D5"
AMBER = "#B87812"
GREEN = "#238568"
PURPLE = "#8B5CF6"


def show_chart(chart, *, height=300):
    chart = (
        chart.properties(height=height, padding={"left": 5, "right": 20, "top": 5, "bottom": 5},
                         autosize=alt.AutoSizeParams(type="fit-x", contains="padding"))
        .configure_view(strokeOpacity=0)
        .configure_axis(
            labelFontSize=12,
            titleFontSize=12,
            labelLimit=210,
        )
        .configure_legend(labelLimit=260,
                          orient="bottom", direction="vertical", columns=1)
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
        .mark_bar(opacity=0.6, orient="vertical")
        .encode(
            x=alt.X(
                "from:Q",
                title=f"{readable_label(field)} · logarithmic scale",
                scale=alt.Scale(type="log"),
            ),
            x2="to:Q",
            y=alt.Y("share:Q", title="Within-group share", axis=alt.Axis(format=".0%")),
            color=alt.Color(
                "label:N", scale=alt.Scale(
                    domain=[label for label, _ in groups],
                    range=[AMBER if label == "Fraud label" else BLUE for label, _ in groups]),
                title="Synthetic label" if by_label else "Population"
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
        alt.Tooltip(x + ":N", title=readable_label(x)),
        alt.Tooltip(y + ":Q", title=readable_label(y), format=".2%" if percentage else ",.2f"),
    ]
    display = frame.assign(_display_label=frame[x].map(wrapped_label).astype(str))
    show_chart(
        alt.Chart(display, description=title or f"{readable_label(y)} by {readable_label(x)}")
        .mark_bar(color=color, cornerRadiusEnd=4)
        .encode(
            y=alt.Y("_display_label:N", sort="-x", title=None,
                    axis=alt.Axis(labelExpr="split(datum.label, '\\n')", labelLimit=230,
                                  labelLineHeight=14)),
            x=alt.X(
                y + ":Q",
                title=title or y.replace("_", " ").title(),
                axis=alt.Axis(format=".0%", tickCount=5) if percentage else alt.Axis(tickCount=5),
            ),
            tooltip=tooltip,
        ), height=max(230, min(720, len(frame) * 42 + 40)),
    )


def fraction(value):
    return "—" if value is None or pd.isna(value) else f"{value:.1%}"


def number(value):
    return "—" if value is None or pd.isna(value) else f"{value:,.0f}"


def evidence_table(frame, label="View chart data"):
    with st.expander(label):
        present_table(frame, width="stretch", hide_index=True)
