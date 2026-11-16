import json

import pandas as pd
import pytest

from frontend.utils.workspace import export_decisions, import_decisions


def snapshot():
    frame = pd.DataFrame({"claim_id": ["A", "B"], "fraud_risk_score": [0.9, 0.7], "risk_rank": [1, 2]})
    meta = {"model_name": "XGBoost", "model_version": "1.0.0", "capacity": 0.03}
    source = [{"claim_id": "A", "claim_amount": 10}, {"claim_id": "B", "claim_amount": 20}]
    raw = export_decisions(frame, meta, source, {"A": "Escalate"}, {"A": "Invoice requires review"}, {"A": "2026-11-15T21:00:00+00:00"})
    return raw, frame, meta, source


def test_decisions_round_trip_without_restoring_trusted_model_scores():
    raw, frame, meta, source = snapshot()
    decisions, notes, stamps = import_decisions(raw, frame, meta, source)
    assert decisions == {"A": "Escalate"}
    assert notes["A"] == "Invoice requires review"
    assert stamps["A"].endswith("+00:00")
    assert "fraud_risk_score" not in json.loads(raw)


@pytest.mark.parametrize("change", ["model", "source", "capacity", "score"])
def test_notes_cannot_silently_attach_to_another_queue(change):
    raw, frame, meta, source = snapshot()
    if change == "model":
        meta["model_version"] = "2.0.0"
    elif change == "capacity":
        meta["capacity"] = 0.1
    elif change == "source":
        source[0]["claim_amount"] = 999
    else:
        frame.loc[0, "fraud_risk_score"] = 0.91
    with pytest.raises(ValueError, match="same portfolio"):
        import_decisions(raw, frame, meta, source)


@pytest.mark.parametrize("corrupt", ["duplicate", "unknown", "decision", "oversized_note", "timestamp"])
def test_rejects_ambiguous_or_invalid_decision_records(corrupt):
    raw, frame, meta, source = snapshot()
    obj = json.loads(raw)
    row = obj["decisions"][0]
    if corrupt == "duplicate":
        obj["decisions"].append(row)
    elif corrupt == "unknown":
        row["claim_id"] = "OUTSIDE_QUEUE"
    elif corrupt == "decision":
        row["decision"] = "Confirmed fraud"
    elif corrupt == "oversized_note":
        row["note"] = "x" * 4001
    else:
        row["updated_at"] = "tomorrow"
    with pytest.raises(ValueError):
        import_decisions(json.dumps(obj).encode(), frame, meta, source)
