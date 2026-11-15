"""Real parsing regressions: ambiguity, allocation bounds, and safe exports."""

import io
import json

import pandas as pd
import pytest

from frontend.utils.data import read_uploaded_file
from health_fraud.config import MAX_BATCH_SIZE, MAX_UPLOAD_BYTES
from health_fraud.data.io import spreadsheet_csv, strict_json_loads


def uploaded(raw: bytes, name: str):
    file = io.BytesIO(raw)
    file.name = name
    return file


@pytest.mark.parametrize(
    "header",
    ["claim_id,claim_amount,claim_amount", 'claim_id,"claim_amount","claim_amount"'],
)
def test_duplicate_csv_header_is_rejected_before_pandas_renaming(header):
    with pytest.raises(ValueError, match="duplicate columns"):
        read_uploaded_file(
            uploaded((header + "\nDUMMY,100,999\n").encode(), "claims.csv")
        )


def test_csv_bom_and_quoted_values_are_supported():
    records = read_uploaded_file(
        uploaded('\ufeffclaim_id,note\nDUMMY,"quoted, text"\n'.encode(), "claims.csv")
    )
    assert records == [{"claim_id": "DUMMY", "note": "quoted, text"}]


def test_csv_mismatched_width_is_rejected():
    with pytest.raises(ValueError, match="width"):
        read_uploaded_file(
            uploaded(b"claim_id,claim_amount\nDUMMY,100,999\n", "claims.csv")
        )


@pytest.mark.parametrize(
    "raw",
    [
        '{"claim_amount":1,"claim_amount":2}',
        '{"nested":{"x":1,"x":2}}',
        '{"x":NaN}',
        '{"x":1e309}',
    ],
)
def test_json_rejects_ambiguity_and_nonfinite_numbers(raw):
    with pytest.raises(ValueError):
        strict_json_loads(raw)


def test_uploaded_json_uses_the_strict_parser():
    with pytest.raises(ValueError, match="Duplicate JSON"):
        read_uploaded_file(uploaded(b'{"claim_id":"A","claim_id":"B"}', "claims.json"))


def test_oversized_file_is_rejected_before_parsing():
    with pytest.raises(ValueError, match="16 MiB"):
        read_uploaded_file(uploaded(b" " * (MAX_UPLOAD_BYTES + 1), "claims.json"))


def test_csv_row_limit_is_checked_before_constructing_the_frame():
    raw = ("claim_id\n" + "DUMMY\n" * (MAX_BATCH_SIZE + 1)).encode()
    with pytest.raises(ValueError, match="row limit"):
        read_uploaded_file(uploaded(raw, "claims.csv"))


def test_parquet_metadata_row_limit():
    file = io.BytesIO()
    pd.DataFrame({"claim_id": range(MAX_BATCH_SIZE + 1)}).to_parquet(file)
    with pytest.raises(ValueError, match="row limit"):
        read_uploaded_file(uploaded(file.getvalue(), "claims.parquet"))


def test_parquet_nested_column_is_rejected():
    file = io.BytesIO()
    pd.DataFrame({"claim_id": ["A"], "nested": [[1, 2]]}).to_parquet(file)
    with pytest.raises(ValueError, match="Nested"):
        read_uploaded_file(uploaded(file.getvalue(), "claims.parquet"))


def test_safe_csv_preserves_numbers_and_literalizes_formulas():
    frame = pd.DataFrame(
        {"note": ["=1+1", " @SUM(1)", "ordinary"], "amount": [-1.0, 2.0, 3.0]}
    )
    result = pd.read_csv(io.BytesIO(spreadsheet_csv(frame)))
    assert result.note.tolist() == ["'=1+1", "' @SUM(1)", "ordinary"]
    assert result.amount.tolist() == [-1.0, 2.0, 3.0]
    assert frame.note.iloc[0] == "=1+1"
