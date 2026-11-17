"""Question-led scientific dashboards; calculations use real bundled artifacts."""

from __future__ import annotations

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from frontend.research.charts import (
    AMBER,
    BLUE,
    GREEN,
    PURPLE,
    bar,
    evidence_table,
    fraction,
    histogram,
    number,
    show_chart,
)
from frontend.research.data import evaluation_frame
from frontend.utils.presentation import present_table, readable_label
from health_fraud.evaluation.metrics import (
    bootstrap_intervals,
    calibration_table,
    capacity_curve,
    metric_summary,
)
from health_fraud.evaluation.quality import distribution_shift, quality_profile


def exploration(frame, corpus, score):
    st.subheader("What does this portfolio contain?")
    st.write(
        f"The median claim is **€{frame.claim_amount.median():,.0f}**; the 95th percentile is **€{frame.claim_amount.quantile(0.95):,.0f}**. The distribution below uses every filtered claim."
    )
    histogram(frame)
    group = (
        frame.groupby("service_category", observed=True)
        .agg(
            claims=("claim_id", "size"),
            claim_value=("claim_amount", "sum"),
            median_amount=("claim_amount", "median"),
            fraud_rate=("is_fraud", "mean"),
        )
        .reset_index()
    )
    left, right = st.columns(2)
    with left:
        bar(group, "service_category", "claims", title="Claims by service")
    with right:
        bar(
            group,
            "service_category",
            "claim_value",
            color=PURPLE,
            title="Submitted value (€)",
        )
    evidence_table(group, "Service statistics")
    candidates = [
        c
        for c in [
            "claim_amount",
            "requested_reimbursement",
            "coverage_limit",
            "service_units",
            "customer_claims_30d",
            "provider_claims_30d",
            "customer_age",
        ]
        if c in frame
    ]
    selected = st.multiselect(
        "Numeric relationships", candidates, default=candidates[:5], max_selections=8, format_func=readable_label
    )
    if len(selected) >= 2:
        correlations = (
            frame[selected].rename(columns=readable_label)
            .corr(method="spearman")
            .rename_axis("first")
            .reset_index()
            .melt(id_vars="first", var_name="second", value_name="spearman")
            .dropna()
        )
        show_chart(
            alt.Chart(
                correlations,
                description="Spearman rank correlations, associations rather than causal effects.",
            )
            .mark_rect()
            .encode(
                x=alt.X("first:N", title=None, axis=alt.Axis(labelAngle=-35)),
                y=alt.Y("second:N", title=None),
                color=alt.Color(
                    "spearman:Q",
                    scale=alt.Scale(domain=[-1, 0, 1], range=[AMBER, "#142239", BLUE]),
                ),
                tooltip=[
                    "first:N",
                    "second:N",
                    alt.Tooltip("spearman:Q", format=".3f"),
                ],
            ),
            height=350,
        )
        st.caption(
            "Spearman correlation describes association. It does not establish why a claim is fraudulent."
        )
        evidence_table(correlations, "Correlation values")


def quality(frame, corpus, score):
    st.subheader("Which data issues are visible and how are they handled?")
    profile = quality_profile(frame)
    st.write(f"**{sum(profile["rules"].values()):,} rule violations** in this cohort. A claim can trigger multiple rules; structural missingness is assessed separately.")
    fields = pd.DataFrame(profile["column_profile"])
    missing = fields.loc[fields.missing > 0].sort_values(
        "missing_rate", ascending=False
    )
    if missing.empty:
        st.success("No missing values in this filtered cohort.")
    else:
        bar(
            missing.head(15),
            "column",
            "missing_rate",
            percentage=True,
            title="Missing values by field",
        )
    st.caption(
        "Absent prior claims or an unrecorded policy change can create structural missingness. These values are not automatically corrupt records."
    )
    evidence_table(fields, "Full field-level quality profile")
    present_table(
        pd.DataFrame(profile["rules"].items(), columns=["Rule", "Flagged rows"]),
        hide_index=True,
        width="stretch",
    )
    if corpus.quality:
        st.markdown("#### Whole-corpus cleaning audit")
        audit = pd.DataFrame(
            [
                {
                    "Stage": name,
                    "Rows": data.get("rows", 0),
                    "Rows with any missing value": data.get(
                        "rows_with_missing_values", 0
                    ),
                }
                for name, data in corpus.quality.items()
                if isinstance(data, dict) and "rows" in data
            ]
        )
        present_table(audit, hide_index=True, width="stretch")
        st.caption(
            "This audit covers the full corpus, independent of exploration filters. The controlled-corruption challenge is separate and never enters model fitting."
        )
        challenge = corpus.quality.get("challenge", {}).get("rules", {})
        if challenge:
            evidence_table(
                pd.DataFrame(
                    challenge.items(),
                    columns=["Controlled challenge rule", "Detected rows"],
                ),
                "Controlled-corruption detections",
            )


def temporal(frame, corpus, score):
    st.subheader("How do volume and outcomes change over time?")
    monthly = (
        frame.assign(
            month=frame.claim_submission_timestamp.dt.to_period("M").dt.to_timestamp()
        )
        .groupby("month")
        .agg(
            claims=("claim_id", "size"),
            claim_value=("claim_amount", "sum"),
            fraud_rate=("is_fraud", "mean"),
        )
        .reset_index()
    )
    monthly["period"] = np.select(
        [
            monthly.month < "2025-07-01",
            monthly.month < "2026-01-01",
            monthly.month < "2026-07-01",
        ],
        ["Training", "Validation", "Reference test"],
        default="Later simulated test",
    )
    chart = (
        alt.Chart(
            monthly,
            description="Monthly claim volume, coloured by the chronological evaluation split.",
        )
        .mark_bar(size=24)
        .encode(
            x=alt.X("month:T", title="Submission month", axis=alt.Axis(format="%b %Y", tickCount="month", labelOverlap=True)),
            y=alt.Y("claims:Q", title="Claims"),
            color=alt.Color(
                "period:N",
                scale=alt.Scale(
                    domain=[
                        "Training",
                        "Validation",
                        "Reference test",
                        "Later simulated test",
                    ],
                    range=[BLUE, PURPLE, GREEN, AMBER],
                ),
                title="Period",
            ),
            tooltip=["month:T", "period:N", "claims:Q"],
        )
    )
    st.write(f"This view contains **{len(monthly)} months** and **{int(monthly.claims.sum()):,} claims**. Changes in label prevalence describe the simulation and do not by themselves demonstrate real-world drift.")
    show_chart(chart)
    show_chart(
        alt.Chart(monthly, description="Observed synthetic fraud prevalence by month.")
        .mark_line(color=AMBER, point=True)
        .encode(
            x=alt.X("month:T", title="Submission month", axis=alt.Axis(format="%b %Y", tickCount="month", labelOverlap=True)),
            y=alt.Y(
                "fraud_rate:Q",
                title="Synthetic fraud prevalence",
                axis=alt.Axis(format=".1%"),
            ),
            tooltip=["month:T", "claims:Q", alt.Tooltip("fraud_rate:Q", format=".2%")],
        )
        .interactive()
    )
    st.caption(
        "Training ends June 2025; validation ends December 2025. January–June 2026 is the published reference horizon. July–October 2026 is a later simulated holdout in the expanded world."
    )
    evidence_table(monthly, "Monthly values and split labels")


def fraud(frame, corpus, score):
    st.subheader("Which patterns distinguish the simulated labels?")
    st.write(f"**{int(frame.is_fraud.sum()):,} of {len(frame):,} claims** carry a simulated fraud label. Compare rates alongside group sizes, rather than treating a pattern as a verdict.")
    histogram(frame, by_label=True)
    group = (
        frame.groupby("service_category", observed=True)
        .agg(
            claims=("claim_id", "size"),
            fraud_cases=("is_fraud", "sum"),
            fraud_rate=("is_fraud", "mean"),
        )
        .reset_index()
    )
    bar(
        group,
        "service_category",
        "fraud_rate",
        color=AMBER,
        percentage=True,
        title="Synthetic fraud prevalence",
    )
    evidence_table(group, "Rates with denominators")
    positive = frame.loc[frame.is_fraud == 1]
    if "fraud_mechanism" in positive and not positive.empty:
        mechanisms = (
            positive.groupby("fraud_mechanism", observed=True)
            .size()
            .rename("cases")
            .reset_index()
        )
        bar(
            mechanisms,
            "fraud_mechanism",
            "cases",
            color=PURPLE,
            title="Labelled fraud mechanisms",
        )
        evidence_table(mechanisms, "Mechanism counts")
    legitimate = frame.loc[frame.is_fraud == 0]
    if "legitimate_anomaly" in legitimate:
        st.write(
            f"**{int(legitimate.legitimate_anomaly.fillna(False).sum()):,}** legitimate-labelled claims contain intentionally unusual behaviour. Large amounts alone are not a fraud verdict."
        )


def models(frame, corpus, score):
    st.subheader("What evidence supports the model and preprocessing choices?")
    report = corpus.report
    if not report:
        st.info(
            "Reproducible experiment results are not available for this corpus yet."
        )
        return
    st.caption(
        "These comparisons use the recorded, fixed 2025-H2 validation cohort. Exploration filters do not change experimental results."
    )
    records = []
    for experiment in report["experiments"]:
        m = experiment["validation_metrics"]
        records.append(
            {
                "Model / experiment": experiment["name"],
                "AP": m["average_precision"],
                "ROC-AUC": m["roc_auc"],
                "Recall @ 3%": m["recall_at_capacity"],
                "Brier": m["brier_score"],
                "Features": experiment["feature_count"],
                "Fit seconds": experiment["fit_seconds"],
            }
        )
    table = pd.DataFrame(records)
    st.write(
        f"Validation-selected candidate: **{report['selected']}**. The live API remains the independently versioned reference model."
    )
    bar(
        table,
        "Model / experiment",
        "AP",
        percentage=False,
        title="Validation Average Precision",
    )
    present_table(
        table.style.format(
            {
                "AP": "{:.4f}",
                "ROC-AUC": "{:.4f}",
                "Recall @ 3%": "{:.1%}",
                "Brier": "{:.4f}",
                "Fit seconds": "{:.2f}",
            }
        ),
        hide_index=True,
        width="stretch",
    )
    selected = st.multiselect(
        "Precision–recall comparison",
        [x["name"] for x in report["experiments"]],
        default=list(
            dict.fromkeys([report["experiments"][0]["name"], report["selected"]])
        ),
    )
    points = pd.DataFrame(
        [
            dict(point, model=e["name"])
            for e in report["experiments"]
            if e["name"] in selected
            for point in e["validation_curve"]
        ]
    )
    if not points.empty:
        show_chart(
            alt.Chart(
                points,
                description="Validation precision–recall curves; metric values use every validation case.",
            )
            .mark_line()
            .encode(
                x=alt.X("recall:Q", title="Recall", axis=alt.Axis(format=".0%")),
                y=alt.Y("precision:Q", title="Precision", axis=alt.Axis(format=".0%")),
                color=alt.Color("model:N", title="Experiment"),
                tooltip=[
                    "model:N",
                    alt.Tooltip("recall:Q", format=".2%"),
                    alt.Tooltip("precision:Q", format=".2%"),
                ],
            )
        )
    learning = pd.DataFrame(report.get("learning_curve", []))
    if not learning.empty:
        long = learning.melt(
            id_vars=["training_claims", "training_period_end"],
            value_vars=["training_ap", "validation_ap"],
            var_name="cohort",
            value_name="AP",
        )
        long["cohort"] = long["cohort"].map(readable_label)
        show_chart(
            alt.Chart(
                long,
                description="Learning curves from growing chronological training prefixes with fixed validation.",
            )
            .mark_line(point=True)
            .encode(
                x=alt.X("training_claims:Q", title="Training examples"),
                y=alt.Y("AP:Q", title="Average Precision"),
                color=alt.Color("cohort:N", title="Evaluation cohort"),
                tooltip=[
                    "training_claims:Q",
                    "training_period_end:N",
                    "cohort:N",
                    alt.Tooltip("AP:Q", format=".4f"),
                ],
            )
        )
        st.caption(
            "Chronological learning curves change both sample size and historical coverage. They do not isolate a purely causal effect of volume."
        )
        evidence_table(learning, "Learning-curve measurements")
    calibration = report.get("calibration_trial", {})
    if calibration:
        st.markdown("#### Separate-period calibration experiment")
        present_table(
            pd.DataFrame(
                [
                    {
                        "Method": name,
                        **{
                            k: m[k]
                            for k in ["average_precision", "brier_score", "log_loss"]
                        },
                    }
                    for name, m in calibration.items()
                    if name in {"raw", "platt"}
                ]
            ),
            hide_index=True,
            width="stretch",
        )
        st.caption(
            "The same development-fitted model is compared raw and calibrated. Platt fitting uses a separate calibration period; evaluation uses validation only."
        )


def capacity(frame, corpus, score):
    st.subheader("What can investigators capture with limited capacity?")
    evaluated = evaluation_frame(frame, score)
    if evaluated.empty:
        st.info(
            "Choose a 2026 test period with available scores. Training-era scores are not used as out-of-time performance."
        )
        return
    percent = st.slider(
        "Investigation capacity (%)", min_value=0.5, max_value=20.0, value=3.0, step=0.5
    )
    metrics = metric_summary(
        evaluated.is_fraud, evaluated[score], evaluated.claim_amount, percent / 100
    )
    cols = st.columns(4)
    for col, label, value in zip(
        cols,
        ["Claims reviewed", "Precision", "Fraud recall", "Fraud amount captured"],
        [
            number(metrics["reviewed"]),
            fraction(metrics["precision_at_capacity"]),
            fraction(metrics["recall_at_capacity"]),
            fraction(metrics["fraud_amount_capture"]),
        ],
    ):
        col.metric(label, value)
    curve = capacity_curve(evaluated.is_fraud, evaluated[score], evaluated.claim_amount)
    long = curve.melt(
        id_vars="review_fraction",
        value_vars=[
            "recall_at_capacity",
            "precision_at_capacity",
            "fraud_amount_capture",
        ],
        var_name="measure",
        value_name="fraction",
    ).dropna()
    long["measure"] = long["measure"].map(readable_label)
    show_chart(
        alt.Chart(
            long,
            description="Review capacity versus precision, fraud recall and fraudulent amount captured.",
        )
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "review_fraction:Q",
                title="Review capacity",
                axis=alt.Axis(format=".0%"),
            ),
            y=alt.Y("fraction:Q", title="Outcome", axis=alt.Axis(format=".0%")),
            color=alt.Color("measure:N", title="Outcome", scale=alt.Scale(
                domain=["Fraud recall", "Review precision", "Fraud amount captured"],
                range=[BLUE, AMBER, GREEN])),
            tooltip=[
                "measure:N",
                alt.Tooltip("review_fraction:Q", format=".1%"),
                alt.Tooltip("fraction:Q", format=".2%"),
            ],
        )
    )
    st.caption(
        f"Computed on {len(evaluated):,} scored out-of-time claims after filters. Captured submitted amounts are not demonstrated cash savings or recovered fraud."
    )
    evidence_table(curve, "Capacity policy measurements")
    cal = calibration_table(evaluated.is_fraud, evaluated[score])
    line = (
        alt.Chart(pd.DataFrame({"x": [0.0, 1.0], "y": [0.0, 1.0]}))
        .mark_line(color="#7E8CA5", strokeDash=[5, 5])
        .encode(x="x:Q", y="y:Q")
    )
    points = (
        alt.Chart(
            cal,
            description="Mean score and observed synthetic fraud frequency by score bin.",
        )
        .mark_line(color=BLUE, point=True)
        .encode(
            x=alt.X("mean_score:Q", title="Mean score", scale=alt.Scale(domain=[0, 1])),
            y=alt.Y(
                "observed_rate:Q",
                title="Observed label frequency",
                scale=alt.Scale(domain=[0, 1]),
            ),
            tooltip=[
                "bin:N",
                "claims:Q",
                alt.Tooltip("mean_score:Q", format=".3f"),
                alt.Tooltip("observed_rate:Q", format=".3f"),
            ],
        )
    )
    show_chart(line + points)
    evidence_table(cal, "Calibration bin counts")


def errors(frame, corpus, score):
    st.subheader("Where does the top-risk review policy make mistakes?")
    evaluated = evaluation_frame(frame, score)
    if evaluated.empty:
        st.info("Select a scored out-of-time cohort first.")
        return
    percent = st.slider("Review capacity for error analysis (%)", 0.5, 20.0, 3.0, 0.5)
    ranked = evaluated.sort_values(score, ascending=False, kind="mergesort").copy()
    selected = np.arange(len(ranked)) < max(
        1, int(np.ceil(len(ranked) * percent / 100))
    )
    ranked["outcome"] = np.select(
        [
            selected & ranked.is_fraud.eq(1),
            selected & ranked.is_fraud.eq(0),
            ~selected & ranked.is_fraud.eq(1),
        ],
        [
            "Captured synthetic fraud",
            "Legitimate case reviewed",
            "Missed synthetic fraud",
        ],
        default="Legitimate case not reviewed",
    )
    counts = ranked.groupby("outcome").size().rename("claims").reset_index()
    bar(counts, "outcome", "claims", title="Capacity-based outcomes")
    kind = st.selectbox(
        "Inspect cases",
        [
            "Missed synthetic fraud",
            "Legitimate case reviewed",
            "Captured synthetic fraud",
        ],
    )
    cases = ranked.loc[ranked.outcome == kind]
    columns = [
        c
        for c in [
            "claim_id",
            "service_category",
            "claim_amount",
            score,
            "fraud_mechanism",
            "fraud_difficulty",
            "customer_claims_30d",
            "provider_claims_30d",
        ]
        if c in cases
    ]
    present_table(cases[columns].head(200), hide_index=True, width="stretch")
    if kind == "Missed synthetic fraud" and not cases.empty:
        mechanisms = (
            cases.groupby("fraud_mechanism", observed=True)
            .size()
            .rename("cases")
            .reset_index()
        )
        bar(
            mechanisms,
            "fraud_mechanism",
            "cases",
            color=AMBER,
            title="Missed mechanisms",
        )
    st.caption(
        "Errors are defined against simulated labels and the selected capacity, not a fixed 0.50 classification threshold. Live Claim Analysis provides TreeSHAP for the published reference model."
    )
    importance = pd.DataFrame(corpus.report.get("candidate_importance", [])).head(15)
    if not importance.empty:
        st.markdown("#### Research candidate feature importance")
        bar(
            importance,
            "feature",
            "importance",
            color=PURPLE,
            title="Candidate model importance",
        )
        st.caption(
            "Model-specific importance from the research candidate; this is distinct from reference-model SHAP and is not a causal explanation."
        )


def robustness(frame, corpus, score):
    st.subheader("How stable are results across populations and time?")
    evaluated = evaluation_frame(frame, score)
    if evaluated.empty:
        st.info("Select scored out-of-time cases for robustness analysis.")
        return
    dimension = st.selectbox(
        "Evaluation subgroup", ["service_category", "provider_region", "coverage_level"], format_func=readable_label
    )
    rows = []
    for name, group in evaluated.groupby(dimension, observed=True, dropna=False):
        metrics = metric_summary(group.is_fraud, group[score], group.claim_amount)
        rows.append(
            {
                "Group": str(name),
                "Claims": len(group),
                "Frauds": int(group.is_fraud.sum()),
                "AP": metrics["average_precision"],
                "Recall @ 3%": metrics["recall_at_capacity"],
                "Brier": metrics["brier_score"],
                "Evidence": "Small subgroup"
                if len(group) < 100 or group.is_fraud.sum() < 5
                else "Sufficient descriptive sample",
            }
        )
    table = pd.DataFrame(rows)
    present_table(table, hide_index=True, width="stretch")
    st.caption(
        "Subgroup differences are descriptive; small positive counts make rankings unstable. Missing or undefined metrics remain blank."
    )
    baseline = corpus.frame.loc[corpus.frame.claim_submission_timestamp < "2025-07-01"]
    drift = pd.DataFrame(
        [
            {"Feature": name, **distribution_shift(baseline[name], evaluated[name])}
            for name in [
                "claim_amount",
                "customer_claims_30d",
                "provider_claims_30d",
                "days_service_to_submission",
            ]
        ]
    )
    st.markdown("#### Reference-quantile distribution shift")
    present_table(drift, hide_index=True, width="stretch")
    st.caption(
        "PSI compares the full training-era reference with the filtered test cohort. It indicates distribution change, not a demonstrated accuracy failure."
    )
    if st.button("Estimate uncertainty for this cohort", type="secondary"):
        with st.spinner("Resampling customer clusters..."):
            result = bootstrap_intervals(
                evaluated.is_fraud,
                evaluated[score],
                evaluated.claim_amount,
                groups=evaluated.customer_id,
                iterations=100,
                seed=42,
            )
        intervals = pd.DataFrame(
            [
                {"Metric": name, "2.5%": value[0], "97.5%": value[1]}
                for name, value in result["intervals"].items()
                if value
            ]
        )
        present_table(intervals, hide_index=True, width="stretch")
        st.caption(
            "95% customer-cluster bootstrap intervals, 100 replicates, seed 42. They describe this synthetic cohort and do not cover the gap to real insurance data."
        )
    scenarios = corpus.report.get("robustness_scenarios", [])
    if scenarios:
        st.markdown("#### Independent simulated worlds")
        present_table(pd.DataFrame(scenarios), hide_index=True, width="stretch")
        for limitation in corpus.report.get("robustness_limitations", []):
            st.caption(limitation)
