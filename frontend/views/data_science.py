"""Question-led scientific evidence with explicit data and model context."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from frontend.components import section_header
from frontend.research import pages
from frontend.research.charts import fraction
from frontend.research.data import available_corpora, load_corpus
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
WORKSPACE_LABELS = dict(zip(WORKSPACES, [
    "Explore", "Data quality", "Timeline", "Fraud patterns", "Models",
    "Capacity", "Errors", "Robustness",
]))


def clear_filters(dataset_id, first, last):
    st.session_state["science_dates_" + dataset_id] = (first, last)
    st.session_state["science_services_" + dataset_id] = []
    st.session_state["science_regions_" + dataset_id] = []


def render(client=None):
    section_header("Data Science Lab", "Explore the data, inspect the methodology and challenge the results.",
                   eyebrow="SCIENTIFIC EVIDENCE", level=1)
    st.caption("Public synthetic research · retrospective evaluation labels · human interpretation required.")
    workspace = st.segmented_control(
        "Analysis workspace", list(WORKSPACES), default="Exploration", required=True,
        format_func=WORKSPACE_LABELS.get, key="science_workspace", wrap=True,
    )
    choices = available_corpora()
    left, right = st.columns(2)
    with left:
        label = st.selectbox("Research corpus", list(choices), key="science_corpus")
    with st.spinner("Preparing verified research data..."):
        corpus = load_corpus(choices[label])
    source = corpus.frame
    score = "reference_score"
    cohort = "Whole corpus"
    with right:
        if workspace == "Model experiments":
            st.caption("Experiments use fixed 2025-H2 validation. Portfolio indicators describe the whole selected corpus.")
        else:
            options = ["Whole corpus", "Reference test · 2026-H1"]
            if source.claim_submission_timestamp.max() >= pd.Timestamp("2026-07-01"):
                options.append("Later simulated test · 2026-H2")
            cohort = st.selectbox("Analysis cohort", options, index=1,
                                  key="science_cohort_" + corpus.name)
    if workspace in {"Investigation capacity", "Explainability & errors", "Robustness & drift"}:
        model = st.radio("Retrospective scoring model", ["Published reference · v1.0.0", "Research candidate · held-out scores"],
                         horizontal=True, key="science_model")
        if model.startswith("Research"):
            score = "candidate_score"
    mask = pd.Series(True, index=source.index)
    services, regions = [], []
    if workspace != "Model experiments":
        if cohort == "Reference test · 2026-H1":
            mask &= source.claim_submission_timestamp.between("2026-01-01", "2026-06-30 23:59:59")
        elif cohort == "Later simulated test · 2026-H2":
            mask &= source.claim_submission_timestamp >= pd.Timestamp("2026-07-01")
        first, last = source.claim_submission_timestamp.min().date(), source.claim_submission_timestamp.max().date()
        with st.expander("Filter dates, services and regions", expanded=False):
            c1, c2, c3 = st.columns(3)
            with c1:
                dates = st.date_input("Submission date range", value=(first, last),
                                      key="science_dates_" + corpus.dataset_id)
            with c2:
                services = st.multiselect("Service categories", sorted(source.service_category.dropna().unique()),
                                          key="science_services_" + corpus.dataset_id, placeholder="All services")
            with c3:
                regions = st.multiselect("Provider regions", sorted(source.provider_region.dropna().unique()),
                                         key="science_regions_" + corpus.dataset_id, placeholder="All regions")
            st.button("Clear filters", on_click=clear_filters, args=(corpus.dataset_id, first, last))
        if len(dates) != 2:
            st.info("Choose both dates to apply the range.")
            return
        mask &= source.claim_submission_timestamp.between(pd.Timestamp(dates[0]),
                    pd.Timestamp(dates[1]) + pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1))
        if services:
            mask &= source.service_category.isin(services)
        if regions:
            mask &= source.provider_region.isin(regions)
    frame = source.loc[mask]
    active = " · ".join([cohort, ", ".join(services) or "All services", ", ".join(regions) or "All regions"])
    st.caption(f"Active view: {active}. {len(frame):,} / {len(source):,} claims.")
    if frame.empty:
        st.info("No cases match these filters. Clear the filters or choose a wider cohort.")
        st.button("Reset empty view", on_click=clear_filters,
                  args=(corpus.dataset_id, source.claim_submission_timestamp.min().date(), source.claim_submission_timestamp.max().date()))
        return
    amount = float(frame.claim_amount.sum())
    with st.container(key="science_kpis"):
        columns = st.columns(4)
        for col, title, value, help_text in zip(columns,
            ["Claims in view", "Fraud prevalence", "Submitted value", "Customers"],
            [f"{len(frame):,}", fraction(float(frame.is_fraud.mean())),
             f"€{amount / 1_000_000:.2f}M" if amount >= 1_000_000 else f"€{amount:,.0f}",
             f"{frame.customer_id.nunique():,}"],
            ["Claims after cohort and exploration filters.", "Share of claims carrying a synthetic fraud label.",
             f"Exact submitted amount: €{amount:,.2f}. This is not recovered fraud or demonstrated savings.",
             "Distinct customers in the active view."]):
            col.metric(title, value, help=help_text)
    with st.expander("Dataset provenance, definitions and exports"):
        st.write(f"Dataset: **{corpus.name}** · fingerprint: `{corpus.dataset_id}` · synthetic data only.")
        st.write("Average precision summarizes precision–recall ranking. Recall is the fraction of labelled fraud selected. Precision is the fraud share of reviewed cases. Review capacity is distinct from an individual score threshold.")
        st.caption("Evaluation labels and simulation mechanisms never enter scoring inputs. Uploaded dossiers are not added to these public research corpora. The live API remains independently versioned.")
        st.download_button("Download filtered sample · up to 1,000 rows", spreadsheet_csv(frame.head(1000)),
                           file_name=f"synthetic_{corpus.name}_sample.csv", mime="text/csv", key="science_download")
    WORKSPACES[workspace](frame, corpus, score)
