"""Bounded input readers and spreadsheet-safe downloads shared by UI and CLI."""

from __future__ import annotations

import csv
import io
import json
import math
from collections import Counter
from typing import Any

import pandas as pd

from health_fraud.config import MAX_BATCH_SIZE, MAX_UPLOAD_BYTES, MAX_UPLOAD_COLUMNS


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON field: {key!r}.")
        result[key] = value
    return result


def _invalid_constant(value: str) -> None:
    raise ValueError(f"Non-finite JSON number {value!r} is not supported.")


def _finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("JSON numbers must be finite.")
    return number


def strict_json_loads(raw: str | bytes) -> Any:
    """Reject ambiguous keys, non-standard constants, and oversized JSON."""
    size = len(raw.encode("utf-8")) if isinstance(raw, str) else len(raw)
    if size > MAX_UPLOAD_BYTES:
        raise ValueError("JSON exceeds the 16 MiB input limit.")
    try:
        return json.loads(
            raw,
            object_pairs_hook=_unique_object,
            parse_constant=_invalid_constant,
            parse_float=_finite_float,
        )
    except RecursionError as exc:
        raise ValueError("JSON nesting is too deep.") from exc


def read_upload_bytes(uploaded: Any) -> bytes:
    """Read at most limit+1 bytes; never trust a client-supplied size alone."""
    if getattr(uploaded, "size", 0) > MAX_UPLOAD_BYTES:
        raise ValueError("File exceeds the 16 MiB upload limit.")
    uploaded.seek(0)
    raw = uploaded.read(MAX_UPLOAD_BYTES + 1)
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    if not isinstance(raw, bytes):
        raise ValueError("Unable to read the uploaded file.")
    if len(raw) > MAX_UPLOAD_BYTES:
        raise ValueError("File exceeds the 16 MiB upload limit.")
    return raw


def read_csv_bounded(raw: bytes) -> pd.DataFrame:
    """Inspect original headers before pandas can rename duplicates."""
    text = raw.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(text))
    header = next(reader, [])
    if not header or not any(name.strip() for name in header):
        raise ValueError("Uploaded CSV contains no header.")
    if any(not name.strip() or name != name.strip() for name in header):
        raise ValueError(
            "CSV headers must be non-empty and have no surrounding spaces."
        )
    duplicates = sorted(name for name, count in Counter(header).items() if count > 1)
    if duplicates:
        raise ValueError("CSV contains duplicate columns: " + ", ".join(duplicates))
    if len(header) > MAX_UPLOAD_COLUMNS:
        raise ValueError(f"CSV exceeds the {MAX_UPLOAD_COLUMNS}-column limit.")
    # Validate row width and count before constructing a potentially wide frame.
    count = 0
    for line, row in enumerate(reader, start=2):
        if not row:
            continue
        if len(row) != len(header):
            raise ValueError(f"CSV row {line} does not match the header width.")
        count += 1
        if count > MAX_BATCH_SIZE:
            raise ValueError(f"CSV exceeds the {MAX_BATCH_SIZE:,}-row limit.")
    return pd.read_csv(
        io.StringIO(text),
        nrows=MAX_BATCH_SIZE + 1,
        dtype={
            name: "string"
            for name in header
            if name
            in {"claim_id", "customer_id", "provider_id", "policy_id", "service_code"}
        },
    )


def read_parquet_bounded(raw: bytes) -> pd.DataFrame:
    """Inspect Parquet metadata and uncompressed size before allocating data."""
    import pyarrow.parquet as pq

    file = pq.ParquetFile(io.BytesIO(raw))
    metadata = file.metadata
    if metadata.num_rows > MAX_BATCH_SIZE:
        raise ValueError(f"Parquet exceeds the {MAX_BATCH_SIZE:,}-row limit.")
    names = file.schema_arrow.names
    if len(names) > MAX_UPLOAD_COLUMNS or len(set(names)) != len(names):
        raise ValueError("Parquet has too many or duplicate columns.")
    if (
        sum(
            metadata.row_group(i).total_byte_size
            for i in range(metadata.num_row_groups)
        )
        > 64 * 1024 * 1024
    ):
        raise ValueError("Parquet exceeds the 64 MiB decoded-size limit.")
    if any(field.type.num_fields for field in file.schema_arrow):
        raise ValueError("Nested Parquet columns are not supported for claim inputs.")
    return file.read().to_pandas()


def spreadsheet_csv(frame: pd.DataFrame) -> bytes:
    """Preserve numeric cells and neutralize formula-like text in a CSV export."""
    safe = frame.copy()

    def neutralize(value: Any) -> Any:
        if isinstance(value, str) and value.lstrip().startswith(
            ("=", "+", "-", "@", "\t", "\r")
        ):
            return "'" + value
        return value

    for column in safe.columns:
        if (
            pd.api.types.is_object_dtype(safe[column])
            or pd.api.types.is_string_dtype(safe[column])
            or isinstance(safe[column].dtype, pd.CategoricalDtype)
        ):
            safe[column] = safe[column].astype(object).map(neutralize)
    safe.columns = [neutralize(str(column)) for column in safe.columns]
    return safe.to_csv(index=False).encode("utf-8-sig")
