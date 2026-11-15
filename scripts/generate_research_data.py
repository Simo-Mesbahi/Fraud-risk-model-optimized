"""Generate a separate reproducible synthetic research corpus."""

import argparse
import json

from health_fraud.data.scenarios import SCENARIOS, materialize_scenario


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/data.yaml")
    parser.add_argument("--output", default="data/research/expanded")
    parser.add_argument("--scenario", choices=SCENARIOS, default="expanded")
    parser.add_argument("--rows", type=int, default=150000)
    parser.add_argument("--seed", type=int, default=1729)
    args = parser.parse_args()
    result = materialize_scenario(
        args.config, args.output, name=args.scenario, rows=args.rows, seed=args.seed
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
