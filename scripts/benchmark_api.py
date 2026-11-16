"""Small local CPU benchmark; never sends a load test to the public demo."""
from __future__ import annotations

import json
import platform
import resource
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from api.app.main import app
from frontend.api_client import FraudAPIClient

ROOT = Path(__file__).resolve().parents[1]


def main():
    frame = pd.read_parquet(ROOT / "data/interim/claims.parquet").sample(1000, random_state=42)
    claims = FraudAPIClient._json_safe(frame.to_dict(orient="records"))
    started = perf_counter()
    measurements = []
    with TestClient(app) as client:
        startup_seconds = perf_counter() - started
        for count in [1, 100, 1000]:
            durations = []
            for iteration in range(4):
                before = perf_counter()
                response = client.post("/score-batch", json={"claims": claims[:count]})
                elapsed = perf_counter() - before
                if response.status_code != 200:
                    raise RuntimeError(str(response.json())[:1500])
                assert len(response.json()["predictions"]) == count
                if iteration:
                    durations.append(elapsed)
            measurements.append({
                "endpoint": "/score-batch", "claims": count,
                "warm_repetitions": len(durations), "median_seconds": float(np.median(durations)),
                "p95_seconds": float(np.quantile(durations, .95)),
                "median_claims_per_second": count / float(np.median(durations)),
            })
        before = perf_counter()
        response = client.post("/explain", json={"claim": claims[0]})
        if response.status_code != 200:
            raise RuntimeError(str(response.json())[:1500])
        measurements.append({"endpoint": "/explain", "claims": 1, "single_measurement_seconds": perf_counter() - before})
    report = {
        "python": platform.python_version(), "platform": platform.platform(),
        "transport": "in-process ASGI TestClient; includes JSON/validation, excludes public network",
        "startup_seconds": startup_seconds,
        "process_peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
        "thread_limits": "OMP_NUM_THREADS=1, OPENBLAS_NUM_THREADS=1",
        "measurements": measurements,
        "limitations": [
            "Local development hardware, three warm repetitions per batch; p95 is descriptive, not a service-level guarantee.",
            "Peak RSS includes this benchmark's pandas data and imports. Render cold starts, concurrency and memory limits require separate production observation.",
        ],
    }
    output = ROOT / "artifacts/benchmarks/local-api.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
