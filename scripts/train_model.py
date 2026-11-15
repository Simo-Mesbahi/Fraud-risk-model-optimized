"""Run chronological model/preprocessing comparisons without replacing production."""

import argparse
from health_fraud.models.train import run_research


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="data/interim/claims.parquet")
    parser.add_argument("--output", default="artifacts/research/reference")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    report = run_research(args.input, args.output, args.seed, args.quick)
    print("Selected:", report["selected"], "(research artifact only)")


if __name__ == "__main__":
    main()
