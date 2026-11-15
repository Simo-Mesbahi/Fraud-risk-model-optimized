"""Evaluate a trusted project candidate on a separately specified labelled corpus."""

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from health_fraud.evaluation.metrics import metric_summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model", required=True, help="Trusted, locally trained joblib artifact only."
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    frame = pd.read_parquet(args.input)
    model = joblib.load(args.model)
    scores = model.predict_proba(frame)[:, 1]
    report = {
        "metrics": metric_summary(frame.is_fraud, scores, frame.claim_amount),
        "data_origin": "Caller-specified; verify external data rights and compatibility separately.",
    }
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
