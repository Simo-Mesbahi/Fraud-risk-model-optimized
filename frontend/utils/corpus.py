"""Compact, read-only public corpora shared across analytical and demo views."""
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]


def read_public_corpus(path):
    """Dictionary-encode repeated strings before allocating pandas objects.

    This loader is only for bundled synthetic assets. User uploads use the
    separate bounded readers and are never retained in this shared cache.
    """
    table = pq.read_table(path, use_threads=False)
    fields = []
    for field in table.schema:
        kind = field.type
        if pa.types.is_integer(kind):
            limits = pc.min_max(table[field.name]).as_py()
            if limits["min"] is not None:
                for candidate, low, high in [
                    (pa.int8(), -128, 127), (pa.int16(), -32768, 32767),
                    (pa.int32(), -2147483648, 2147483647),
                ]:
                    if low <= limits["min"] <= limits["max"] <= high:
                        kind = candidate
                        break
        fields.append(field.with_type(kind))
    table = table.cast(pa.schema(fields, metadata=table.schema.metadata))
    categories = [
        field.name for field in table.schema
        if field.name != "claim_id"
        and (pa.types.is_string(field.type) or pa.types.is_large_string(field.type))
    ]
    frame = table.to_pandas(
        categories=categories, split_blocks=True, self_destruct=True, use_threads=False
    )
    del table
    pa.default_memory_pool().release_unused()
    return frame


@st.cache_resource(show_spinner=False, max_entries=1)
def reference_claims():
    return read_public_corpus(ROOT / "data/interim/claims.parquet")
