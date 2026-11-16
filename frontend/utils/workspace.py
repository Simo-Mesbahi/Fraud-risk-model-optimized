"""Portable investigator notes, bound to an already scored queue, never trusted scores."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from health_fraud.data.io import strict_json_loads

DECISIONS = {"Pending review", "Investigate", "Escalate", "Clear"}
MAX_SNAPSHOT_BYTES = 2 * 1024 * 1024


def queue_fingerprint(frame, metadata, source_claims):
    """Bind notes to model identity, capacity, source records and selected scores."""
    import pandas as pd

    source = pd.DataFrame(source_claims).sort_values("claim_id", kind="stable")
    source = source.reindex(sorted(source.columns), axis=1)
    ranked = frame[["claim_id", "fraud_risk_score", "risk_rank"]].sort_values("risk_rank")
    identity = {
        "model_name": metadata.get("model_name"),
        "model_version": metadata.get("model_version"),
        "capacity": metadata.get("capacity"),
        "source": source.to_json(orient="records", date_format="iso", double_precision=15),
        "selection": ranked.to_json(orient="records", double_precision=15),
    }
    return hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()


def export_decisions(frame, metadata, source_claims, decisions, notes, timestamps):
    records = []
    for claim_id in frame.claim_id.astype(str):
        if claim_id in decisions or notes.get(claim_id):
            records.append({
                "claim_id": claim_id,
                "decision": decisions.get(claim_id, "Pending review"),
                "note": notes.get(claim_id, ""),
                "updated_at": timestamps.get(claim_id, ""),
            })
    payload = {
        "schema_version": "1.0.0",
        "queue_fingerprint": queue_fingerprint(frame, metadata, source_claims),
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "decisions": records,
    }
    result = json.dumps(payload, ensure_ascii=False, allow_nan=False, indent=2).encode()
    if len(result) > MAX_SNAPSHOT_BYTES:
        raise ValueError("Decision snapshot exceeds 2 MiB. Export the worklist CSV instead.")
    return result


def import_decisions(raw, frame, metadata, source_claims):
    if len(raw) > MAX_SNAPSHOT_BYTES:
        raise ValueError("Decision snapshot exceeds 2 MiB.")
    data = strict_json_loads(raw)
    if not isinstance(data, dict) or set(data) != {
        "schema_version", "queue_fingerprint", "exported_at", "decisions"
    }:
        raise ValueError("Unsupported decision snapshot structure.")
    if data["schema_version"] != "1.0.0":
        raise ValueError("Unsupported snapshot version.")
    if data["queue_fingerprint"] != queue_fingerprint(frame, metadata, source_claims):
        raise ValueError("Regenerate the same portfolio, capacity and model before importing these decisions.")
    records = data["decisions"]
    if not isinstance(records, list) or len(records) > len(frame):
        raise ValueError("Invalid decision list.")
    valid_ids = set(frame.claim_id.astype(str))
    decisions, notes, timestamps = {}, {}, {}
    for row in records:
        if not isinstance(row, dict) or set(row) != {"claim_id", "decision", "note", "updated_at"}:
            raise ValueError("Invalid decision record.")
        identifier = row["claim_id"]
        if not isinstance(identifier, str) or identifier not in valid_ids or identifier in decisions:
            raise ValueError("Unknown or duplicate claim identifier.")
        if not isinstance(row["decision"], str) or row["decision"] not in DECISIONS:
            raise ValueError("Unknown investigator decision.")
        if not isinstance(row["note"], str) or len(row["note"]) > 4000:
            raise ValueError("Investigator notes must be text with at most 4,000 characters.")
        stamp = row["updated_at"]
        if not isinstance(stamp, str) or len(stamp) > 64:
            raise ValueError("Invalid decision timestamp.")
        if stamp:
            try:
                datetime.fromisoformat(stamp)
            except ValueError as error:
                raise ValueError("Invalid decision timestamp.") from error
        decisions[identifier], notes[identifier], timestamps[identifier] = row["decision"], row["note"], stamp
    return decisions, notes, timestamps


def render_decision_workspace(frame, metadata, source_claims):
    import streamlit as st

    with st.expander("Save & resume investigator decisions"):
        st.caption(
            "Download notes to your device. To resume later, regenerate the same queue, then import this JSON. "
            "The file contains editable human decisions; model scores are always obtained from the API. "
            "Uploads and notes remain in your current session."
        )
        raw = export_decisions(
            frame, metadata, source_claims,
            st.session_state.queue_human_decisions,
            st.session_state.queue_human_notes,
            st.session_state.queue_decision_timestamps,
        )
        st.download_button("Save investigator decisions", raw, "investigator-decisions.json", "application/json")
        upload = st.file_uploader("Resume decisions JSON (2 MiB maximum)", type=["json"], key="queue_resume_file")
        if st.button("Restore decisions", disabled=upload is None):
            try:
                restored = import_decisions(upload.getvalue(), frame, metadata, source_claims)
            except (ValueError, UnicodeError) as error:
                st.error(str(error))
            else:
                for key, values in zip(
                    ["queue_human_decisions", "queue_human_notes", "queue_decision_timestamps"], restored
                ):
                    st.session_state[key].update(values)
                for index, row in st.session_state.queue_results.iterrows():
                    identifier = str(row.claim_id)
                    if identifier in restored[0]:
                        for column, values in zip(
                            ["human_decision", "investigator_note", "decision_updated_at"], restored
                        ):
                            st.session_state.queue_results.at[index, column] = values[identifier]
                        for prefix in ["decision_", "note_"]:
                            st.session_state.pop(prefix + identifier, None)
                st.session_state.queue_resume_notice = len(restored[0])
                st.rerun()
