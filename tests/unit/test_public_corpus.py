import pandas as pd

from frontend.utils.corpus import read_public_corpus


def test_compact_reader_preserves_claim_values_and_missing_context(tmp_path):
    original = pd.DataFrame({
        "claim_id": ["A", "B", "C"], "provider_id": ["P1", None, "P1"],
        "service_category": ["dental", "optical", "dental"],
        "service_units": [1, 255, 128],
        "claim_amount": [123.45, 20.0, 99.99], "document_count": [2.0, None, 1.0],
        "submitted": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-03"]),
    })
    path = tmp_path / "claims.parquet"
    original.to_parquet(path, index=False)
    actual = read_public_corpus(path)
    pd.testing.assert_frame_equal(actual.astype(object), original.astype(object))
    assert isinstance(actual.provider_id.dtype, pd.CategoricalDtype)
    assert actual.claim_id.tolist() == ["A", "B", "C"]
