# Fraud Risk Decision Support Platform

A public, account-free portfolio project demonstrating data analysis, temporal machine learning and human investigation workflows on **synthetic health-insurance claims**.

[Open the application](https://mesbahi-fraud-risk-model-app.onrender.com) · [API documentation](https://mesbahi-fraud-risk-model.onrender.com/docs) · [Implementation checklist](docs/implementation-plan.md) · [Research methodology](docs/research-methodology.md)

The platform ranks claims within an investigation budget and explains the published XGBoost model with TreeSHAP. A risk score supports human review; it does not establish fraud. The results below describe simulated data, not performance at an insurer.

## Explore the evidence

Seven application pages connect the data-science work to its practical use:

| Page | What a reviewer can inspect |
|---|---|
| Overview | Business objective, published model and review policy |
| **Data Science Lab** | Eight analytical workspaces, two identifiable corpora, filters and downloadable evidence |
| Claim Analysis | Guided point-in-time feature construction, historical demo and JSON input; API scoring and local SHAP |
| Portfolio Scoring | Bounded CSV/JSON/Parquet imports, scoring and deterministic portfolio ranking |
| Investigation Queue | Adjustable capacity, human decisions, notes, formula-safe CSV and local decision snapshots |
| Model Insights | Published performance and global/local model interpretation |
| System Status | Live API readiness and model contract |

The Data Science Lab covers **exploration, quality, time, fraud mechanisms, model experiments, investigation capacity, explainability/errors, and robustness/drift**. Charts have table alternatives and state their denominators. Retrospective labels are used for evaluation and excluded from inference.

## Published reference and research candidates

The published model remains **XGBoost v1.0.0**, with 57 engineered input features and 107 transformed features. Its frozen artifacts and original reports remain identifiable.

| Published reference, January–June 2026 | Result |
|---|---:|
| Held-out claims / fraudulent labels | 14,176 / 409 |
| Average Precision / ROC-AUC | 0.5520 / 0.8518 |
| Brier score / log loss | 0.0174 / 0.0797 |
| Review budget | 3%, rounded up to 426 claims |
| Fraud recall / precision at that budget | 53.79% / 51.64% |
| Lift / fraudulent claim amount captured | 17.90× / 55.15% |

These are the published baseline results. The executable research pipeline separately compares eight choices: Dummy, logistic regression, random forest, XGBoost, scaling and imputation alternatives, additional features and history ablation.

| Corpus | Accepted claims | Selected research candidate | Candidate AP, 2026-H1 | Candidate AP, 2026-H2 |
|---|---:|---|---:|---:|
| Published reference | 99,911 | XGBoost, reference features | 0.5513 | No later data |
| Expanded longitudinal simulation, seed 1729 | 149,841 | XGBoost without scaling | 0.5525 | 0.5065 |

Selection uses **validation-period AP**, followed by recall at 3% and lower Brier score for ties. Test results do not select the model. The already-published reference test is a regression benchmark, not a newly untouched dataset. The later expanded test is simulated future data. Differences between corpora do not isolate a causal effect of adding rows.

Additional candidate features did **not** improve validation AP in these runs. Historical-feature ablation materially reduced it. Both positive and negative findings are retained in [reference](artifacts/research/reference/report.json) and [expanded](artifacts/research/expanded/report.json) reports. Research candidates are **not silently promoted** into the live scoring API.

## Reproduce the work

Use Python **3.12**. Role-specific locks contain exact direct/transitive versions and package hashes; the CPU XGBoost distribution avoids downloading CUDA runtimes.

```bash
git clone https://github.com/Simo-Mesbahi/Fraud-risk-model-optimized.git
cd Fraud-risk-model-optimized
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --require-hashes -r requirements/dev.lock
python -m pip install --no-deps --no-build-isolation -e .
python scripts/fetch_research_assets.py
```

Large synthetic analytical assets are distributed in an immutable project release. The [manifest](configs/research-assets.json) pins each asset's size and SHA-256; invalid downloads fail before installation. Reference inference artifacts remain in Git.

```bash
# Two terminals; the frontend talks to the same API as programmatic clients.
PYTHONPATH=.:src python -m uvicorn api.app.main:app --host 0.0.0.0 --port 8000
PYTHONPATH=.:src FRAUD_API_URL=http://127.0.0.1:8000 streamlit run frontend/app.py
```

To regenerate research rather than download it:

```bash
PYTHONPATH=.:src python scripts/generate_research_data.py --help
PYTHONPATH=.:src OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python scripts/generate_research_data.py --output data/research/expanded --rows 150000 --seed 1729
PYTHONPATH=.:src OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python scripts/train_model.py --input data/research/expanded/claims.parquet --output artifacts/research/expanded
PYTHONPATH=.:src python scripts/evaluate_model.py --help
```

See the command help and [methodology](docs/research-methodology.md) for the temporal cutoffs, calibration trial, independent scenarios, fingerprints and limits. Regenerating a report never replaces the published model. Do not load untrusted joblib/pickle artifacts.

## Contracts and safeguards

| Boundary | Behavior |
|---|---|
| Source record | Typed business validation, finite values, dates/count consistency and rebuilt ratios |
| Historical features | Shared batch/online rules; strictly previous timestamps, including simultaneous-claim handling |
| Policy context | Effective events and service-specific coverage; context provenance is exposed |
| Uploads and API | 16 MiB input, 10,000 claims, 96 columns; duplicate keys/columns/IDs rejected |
| Parquet | Metadata row/column and 64 MiB decoded-size bounds before loading; flat columns only |
| Public API | Four simultaneous inference requests per process; busy requests receive 429/Retry-After |
| Client | Bounded timeouts, GET retries, no automatic scoring POST replay |
| Human decisions | Session-local; portable notes attach only to the same source, capacity and model fingerprint |
| Exports | CSV text that could execute as a spreadsheet formula is escaped |
| Diagnostics | Generic public page errors with a reference; details stay in server logs |

The live model consumes an **enriched source record**, not an arbitrary four-field claim. Use a provided demo record or guided intake. The complete [API contract](docs/api-contract.md) describes this boundary.

## Quality and deployment

```bash
PYTHONPATH=.:src python -m pytest tests -q
PYTHONPATH=.:src python -m pytest api/tests -q
ruff check .
mypy
python scripts/fetch_research_assets.py --verify-only
```

GitHub Actions checks dependency consistency, lint, critical-module typing, numerical/contract/UI tests and a **75% coverage gate across the declared serving, research and utility modules**. It also builds both Docker images and exercises the browser against the running container stack. Run the browser checks locally after installing Chromium with Playwright:

```bash
python -m playwright install chromium
python scripts/browser_smoke.py
```

Both images pin the Python base digest, use hash-checked dependency locks, run without root and forward termination signals to the application process. `docker compose up --build -d` starts the stack. [render.yaml](render.yaml) documents the two existing free-tier Frankfurt services; it does not require creating another stack. Git-linked auto-deploys wait for checks to pass.

Local benchmark measurements, their environment and limitations are recorded in [local-api.json](artifacts/benchmarks/local-api.json) and [frontend-data-memory.json](artifacts/benchmarks/frontend-data-memory.json). Public datasets share compact, read-only buffers; score joins avoid duplicating the complete corpus. The container workflow checks the real browser with a 512 MiB memory limit per service. These measurements are not Render latency or concurrency guarantees. Free-tier services can sleep and need a cold start. Horizontal replicas would each have their own admission limit and session state; distributed rate limiting and external state are required before real multi-user scaling.

## Scope and next evidence

All bundled data are synthetic. User uploads and investigator notes belong to the active Streamlit session; optional exports are stored on the user's device. No account system is required for the recruiter demonstration. Avoid uploading real medical or personal information to this public demo.

A compatible, licensed, independently labelled external insurance dataset would enable a separate validation protocol. It is **not** fabricated or mixed into these experiments. A real insurer deployment additionally requires operational governance, privacy controls, independent validation, monitoring and explicitly reviewed model promotion.

**Mohammed El Mesbahi** · Data Science & Artificial Intelligence
# Public demonstration and interface

The demonstration starts with an executive overview and two direct paths: explore the
synthetic research or score a claim. Navigation groups discovery, analysis and
investigation. Completed scores appear before the intake form; scored portfolios can
be handed to the investigation queue without another upload. Human decisions and
save/resume controls remain separate from model recommendations.

`Data Science Lab` exposes eight visible analytical workspaces with explicit corpus,
cohort, model and filter context. Reference validation charts are generated by
`scripts/build_demo_evidence.py` from the exact frozen test cohort. The builder checks
average precision and ROC-AUC against recorded model metrics. Archived scientific
figures remain available unchanged. Curve plots contain up to 250 display points;
metrics use every evaluation claim.

The Render frontend runs `scripts/serve_demo.py` with `FRAUD_INFERENCE_MODE=embedded`.
FastAPI and Streamlit share an interpreter; the scoring listener binds only to
`127.0.0.1:8800`. The interface starts after the real model reports ready. This removes
the second public-network wake-up dependency from interactive demonstrations. The
standalone API image remains independently deployable. For separate services, set
`FRAUD_INFERENCE_MODE=remote` and `FRAUD_API_URL` to the intended API endpoint.

Free Render instances can still sleep: the first interface visit can include the
hosting platform's wake-up screen. This project does not claim always-on availability
or real-insurance validation. No paid hosting upgrade is required by this change.

The combined demo dependency lock is the checked union of the existing tested API and
frontend locks; regenerate it with `python scripts/lock_dependencies.py --demo-only`.
CI builds both containers, limits each to 512 MiB, checks scoring/TreeSHAP and
investigator save/resume, and captures desktop, 390 px and 768 px interface evidence.
