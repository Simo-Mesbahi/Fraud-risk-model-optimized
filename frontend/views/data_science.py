"""Recruiter-facing scientific evidence with progressive analytical navigation."""

import pandas as pd
import streamlit as st

from frontend.components import section_header
from frontend.research.charts import fraction
from frontend.research.data import available_corpora, load_corpus
from frontend.research import pages
from health_fraud.data.io import spreadsheet_csv

WORKSPACES = {
    "Exploration": pages.exploration,
    "Data quality": pages.quality,
    "Time & evaluation splits": pages.temporal,
    "Fraud patterns": pages.fraud,
    "Model experiments": pages.models,
    "Investigation capacity": pages.capacity,
    "Explainability & errors": pages.errors,
    "Robustness & drift": pages.robustness,
}


def render(client=None):
    section_header(
        "Data Science Lab",
        "Explore the data, inspect the methodology and challenge the results.",
        eyebrow="SCIENTIFIC EVIDENCE",
    )
    st.caption(
        "Public synthetic research · retrospective labels are used for evaluation only · the live scoring API remains independently versioned."
    )
    choices = available_corpora()
    left, right = st.columns([1, 1])
    with left:
        label = st.selectbox("Research corpus", list(choices), key="science_corpus")
    with right:
        workspace = st.selectbox(
            "Analysis workspace", list(WORKSPACES), key="science_workspace"
        )
    with st.spinner("Checking dataset provenance..."):
        corpus = load_corpus(choices[label])
    source = corpus.frame
    score = "reference_score"
    if workspace in {
        "Investigation capacity",
        "Explainability & errors",
        "Robustness & drift",
    }:
        model = st.radio(
            "Retrospective scoring model",
            ["Published reference · v1.0.0", "Research candidate · held-out scores"],
            horizontal=True,
            key="science_model",
        )
        if model.startswith("Research"):
            score = "candidate_score"
    frame = source
    if workspace != "Model experiments":
        options = ["Whole corpus", "Reference test · 2026-H1"]
        if source.claim_submission_timestamp.max() >= pd.Timestamp("2026-07-01"):
            options.append("Later simulated test · 2026-H2")
        cohort = st.radio(
            "Analysis cohort",
            options,
            index=1,
            horizontal=True,
            key="science_cohort_" + corpus.name,
        )
        mask = pd.Series(True, index=source.index)
        if cohort == options[1]:
            mask &= source.claim_submission_timestamp.between(
                "2026-01-01", "2026-06-30 23:59:59"
            )
        elif len(options) > 2 and cohort == options[2]:
            mask &= source.claim_submission_timestamp >= pd.Timestamp("2026-07-01")
        with st.expander("Filter dates, services and regions", expanded=False):
            c1, c2, c3 = st.columns(3)
            with c1:
                dates = st.date_input(
                    "Submission date range",
                    value=(
                        source.claim_submission_timestamp.min().date(),
                        source.claim_submission_timestamp.max().date(),
                    ),
                    key="science_dates_" + corpus.dataset_id,
                )
            with c2:
                services = st.multiselect(
                    "Service categories",
                    sorted(source.service_category.dropna().unique()),
                    key="science_services_" + corpus.dataset_id,
                    placeholder="All services",
                )
            with c3:
                regions = st.multiselect(
                    "Provider regions",
                    sorted(source.provider_region.dropna().unique()),
                    key="science_regions_" + corpus.dataset_id,
                    placeholder="All regions",
                )
        if len(dates) != 2:
            st.info("Choose both dates to apply the range.")
            return
        mask &= source.claim_submission_timestamp.between(
            pd.Timestamp(dates[0]),
            pd.Timestamp(dates[1]) + pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1),
        )
        if services:
            mask &= source.service_category.isin(services)
        if regions:
            mask &= source.provider_region.isin(regions)
        frame = source.loc[mask]
    if frame.empty:
        st.info(
            "No cases match these filters. Widen the period or remove a category filter."
        )
        return
    columns = st.columns(4)
    for col, title, value in zip(
        columns,
        [
            "Claims in view",
            "Synthetic fraud prevalence",
            "Submitted claim value",
            "Customers",
        ],
        [
            f"{len(frame):,}",
            fraction(float(frame.is_fraud.mean())),
            f"€{frame.claim_amount.sum():,.0f}",
            f"{frame.customer_id.nunique():,}",
        ],
    ):
        col.metric(title, value)
    st.divider()
    WORKSPACES[workspace](frame, corpus, score)
    with st.expander("Dataset provenance, definitions and exports"):
        st.write(
            f"Dataset fingerprint: `{corpus.dataset_id}` · dataset: `{corpus.name}` · synthetic data only."
        )
        st.write(
            "Average Precision summarizes precision–recall ranking. Recall is the share of labelled fraud selected. Precision is the fraud share of reviewed cases. Capacity is the selected fraction, distinct from an individual score threshold."
        )
        st.caption(
            "Scoring inputs exclude ground truth, fraud mechanisms, difficulty labels and synthetic latent scores. The analytical views deliberately expose those retrospective labels to evaluate the simulation."
        )
        sample = frame.head(1000)
        st.download_button(
            "Download filtered sample · up to 1,000 rows",
            spreadsheet_csv(sample),
            file_name=f"synthetic_{corpus.name}_sample.csv",
            mime="text/csv",
            key="science_download",
        )
        st.caption(
            "Uploaded operational dossiers are not added to these shared analytical corpora. These views use bundled public synthetic datasets only."
        )
