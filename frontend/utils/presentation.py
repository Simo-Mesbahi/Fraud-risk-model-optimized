"""Business labels and display formatting; analytical values stay unchanged."""
from __future__ import annotations

import re
import textwrap

import pandas as pd
import streamlit as st

LABELS = {
    "AP": "Average precision", "average_precision": "Average precision",
    "candidate_AP": "Candidate average precision", "published_model_AP": "Reference average precision",
    "roc_auc": "ROC-AUC", "brier_score": "Brier score", "log_loss": "Log loss",
    "claim_id": "Claim ID", "customer_id": "Customer ID", "provider_id": "Provider ID",
    "claim_amount": "Claim amount (€)", "requested_reimbursement": "Requested reimbursement (€)",
    "coverage_limit": "Coverage limit (€)", "service_units": "Service units",
    "service_category": "Service category", "provider_region": "Provider region",
    "coverage_level": "Coverage level", "fraud_mechanism": "Fraud mechanism",
    "fraud_difficulty": "Fraud difficulty", "is_fraud": "Synthetic fraud label",
    "reference_score": "Reference risk score", "candidate_score": "Candidate risk score",
    "fraud_risk_score": "Risk score", "claim_value": "Submitted value (€)",
    "median_amount": "Median amount (€)", "fraud_rate": "Synthetic fraud prevalence",
    "missing_rate": "Missing values", "missing": "Missing values", "column": "Field",
    "claim_to_service_median_ratio": "Amount / typical service amount",
    "days_since_customer_previous_claim": "Days since previous customer claim",
    "reimbursement_ratio": "Requested / claim amount",
    "requested_to_limit_ratio": "Requested / coverage limit",
    "amount_above_service_typical": "Amount above service benchmark",
    "days_service_to_submission": "Days from service to submission",
    "fraud_amount_capture": "Fraud amount captured", "fraud_amount_captured": "Fraud amount captured",
    "recall_at_capacity": "Fraud recall", "precision_at_capacity": "Review precision",
    "candidate_recall_at_3pct": "Candidate recall at 3%", "review_fraction": "Review capacity",
    "customer_provider_pattern": "Customer–provider pattern", "amount_inflation": "Amount inflation",
    "frequency_abuse": "Frequency abuse", "provider_abnormality": "Unusual provider activity",
    "repeated_service": "Repeated service", "mixed_pattern": "Mixed pattern",
    "training_ap": "Training average precision", "validation_ap": "Validation average precision",
    "psi": "Distribution shift (PSI)", "reference": "Reference claims", "current": "Evaluated claims",
    "claims_generated": "Generated claims", "claims_evaluated": "Evaluated claims",
    "fraud_prevalence": "Synthetic fraud prevalence", "hard_cases": "Harder fraud cases",
    "population_shift": "Population shift", "missing_evidence": "Missing evidence",
    "same_service_claims_30d": "Same-service claims · 30 days",
    "customer_provider_claims_30d": "Customer–provider claims · 30 days",
}


def readable_label(value: object) -> str:
    raw = str(value)
    name = re.sub(r"^(numeric|categorical)__", "", raw)
    if name in LABELS:
        return LABELS[name]
    if "_" not in name:
        return name
    name = re.sub(r"_(\d+)d\b", r" · \1 days", name)
    return name.replace("_", " ").capitalize()


def wrapped_label(value: object, width: int = 28) -> str:
    return "\n".join(textwrap.wrap(readable_label(value), width, break_long_words=False))


def present_table(frame, **kwargs) -> None:
    """Keep numeric sort/export semantics while exposing readable column labels."""
    data = frame.data if hasattr(frame, "data") and isinstance(frame.data, pd.DataFrame) else frame
    if not isinstance(data, pd.DataFrame):
        st.dataframe(frame, **kwargs)
        return
    config = {str(c): st.column_config.Column(readable_label(c)) for c in data.columns}
    config.update(kwargs.pop("column_config", {}) or {})
    if isinstance(frame, pd.DataFrame):
        formats = {}
        for col in data.select_dtypes(include="number").columns:
            name = str(col).lower()
            if name in {"fraction", "review_fraction"} or any(part in name for part in ["precision", "recall", "prevalence", "rate", "share", "capture", "score"]):
                formats[col] = "{:.1%}" if name not in {"average_precision", "brier_score"} else "{:.4f}"
            elif name in {"ap", "candidate_ap", "published_model_ap", "roc_auc", "brier", "psi", "log_loss"}:
                formats[col] = "{:.4f}"
            elif pd.api.types.is_integer_dtype(data[col]):
                formats[col] = "{:,.0f}"
            else:
                formats[col] = "{:,.2f}"
        for col in data.columns:
            if str(col).lower() in {"feature", "column", "rule", "controlled challenge rule", "fraud_mechanism"}:
                formats[col] = readable_label
        frame = data.style.format(formats, na_rep="—")
    st.dataframe(frame, column_config=config, **kwargs)


def go_to(page: str, **state) -> None:
    """Preserve a clear, session-local handoff between product workspaces."""
    for key, value in state.items():
        st.session_state[key] = value
    st.session_state["main_navigation"] = page


def section_links(items: dict[str, str]) -> None:
    links = " · ".join(f"[{label}](#{anchor})" for label, anchor in items.items())
    st.markdown(links)
