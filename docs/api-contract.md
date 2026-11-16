# Enriched source-claim API contract

`/score` and `/explain` accept a `claim` object. `/score-batch` and `/top-review` accept a non-empty `claims` list of at most 10,000 records. `/top-review` also accepts `review_fraction` in (0, 1]; `/explain` accepts `top_k` from 1 to 50. Refer to `/docs` for exact request/response shapes.

The source record includes claim identifiers, service details/dates, amount/reimbursement/coverage, customer and policy context, provider context, evidence flags and point-in-time historical counts/averages. The authoritative field definitions and business rules are in `src/health_fraud/data/contracts.py`. Guided UI intake builds this enriched record from the bundled synthetic context; a raw claim alone cannot invent its historical aggregates.

Nulls are permitted for documented absent context, including a missing provider, missing prescription/document evidence and unavailable prior averages. Historical counts must be nonnegative and monotonic across customer 7/30/90/365-day windows and provider 30/90-day windows. Relationship counts cannot exceed the customer window. Dates are normalized to UTC-naive instants; service date cannot be after submission date. Reimbursement cannot exceed the amount or effective coverage, allowing one cent for rounding.

Derived submission date, service delay and amount ratios are rebuilt at ingestion. Synthetic target/analysis fields and extra scalar context are discarded before inference. Nested values, excessive field lengths, duplicate identifiers in a batch and nonfinite numeric JSON values are rejected. Malformed records return 422 with field locations and safe descriptions rather than an internal model failure. Validation responses omit the submitted record.

Total request bodies are bounded to 16 MiB before JSON processing. Each inference process admits four simultaneous POST requests, with a 15-second timeout per body receive operation; a busy process returns 429 and `Retry-After: 2`. This admission control is process-local, not a global distributed quota. GET health remains available while inference capacity is occupied.

The score is produced by the frozen XGBoost/preprocessor pair. Risk bands describe the score; review selection instead depends on the rank of a claim inside its submitted portfolio and the selected capacity. The same score may be selected in one portfolio and unselected in another. Stable ties preserve input order. Human decisions do not change the model output.

The API client has separate connection/read timeouts. Transient GET failures can be retried; scoring POSTs are not replayed after a server response. Current requests are stateless. Uploaded portfolios and investigator notes are session-local in the frontend. The portable JSON contains human decisions and a queue fingerprint, not trusted model scores; re-score the same portfolio/model/capacity before restoring it.
