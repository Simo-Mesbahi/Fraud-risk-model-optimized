# Research protocol and interpretation

## Dataset identity

The reference corpus has 100,000 requested claims, 99,911 accepted and 89 rejected. The v4 expanded corpus has 150,000 requested, 149,841 accepted and 159 rejected, generated with seed 1729. These are separate synthetic worlds; their entity identifiers are not links between worlds.

The v4 simulation adds synthetic birth/join dates and one dated policy event per affected policy. Service coverage and policy tenure are evaluated as of claim submission. Historical windows use strictly earlier timestamps. Claims at the same timestamp cannot enter one another's histories. Fraud mechanisms and plausible legitimate anomalies overlap intentionally. Missing historical averages can be structural.

Quality reports preserve raw, clean, rejected and deliberately corrupted stages. The 600-row challenge fixture is never used for training. SHA-256 hashes and resolved configuration identify generated tables. The canonical source revision in the reports has the same Git tree as the original local experiment checkpoint; the local revision is retained separately.

## Temporal protocol

| Partition | Submission dates | Purpose |
|---|---|---|
| Train | Before 2025-07-01 | Fit preprocessing and model |
| Validation | 2025-07-01 through 2025-12-31 | Select candidate by AP, recall at 3%, then lower Brier |
| Reference test | 2026-01-01 through 2026-06-30 | Evaluate after selection |
| Later simulated test | From 2026-07-01, where available | Evaluate sensitivity to a later period |

Imputation, scaling and category encoding are fitted on training rows only during comparisons. Selected candidates are refitted on train plus validation before test scoring. Identifiers, labels, latent probabilities, synthetic behavior segments and fraud mechanisms cannot be selected as predictors. Online histories are computed before scoring. This is an out-of-time, existing-population evaluation; it is not an unseen-customer/provider holdout, and label availability delay is not simulated.

## Comparisons

Eight experiments examine model families, scaling, imputation, four extra features and removal of historical features. The extra features remain research-only. Validation AP determines selection; the test is not used to pick a winning pipeline. The committed reports contain parameters, measured validation metrics, prediction curves and final test metrics.

Learning curves use chronological prefixes of the training period and a fixed validation cohort. More rows also mean broader time coverage, so a change cannot be attributed solely to volume. A separate calibration trial fits Platt scaling on April–June 2025 after a development fit ending March 2025, then evaluates on validation. Calibration is not silently applied to the published model.

Six independent-world checks combine hard cases, population shift and missing evidence with seeds 2718 and 31415. Each requests 20,000 claims, evaluates 2026 dates and scores frozen candidates without fitting or selecting on the scenario. The smaller worlds also change historical density. These are sensitivity tests, not controlled causal effects or real insurance validation.

## Metrics and uncertainty

Average Precision handles score ties exactly. ROC-AUC uses average ranks. Capacity uses `ceil(n × fraction)` and stable input order to break ties. Precision, recall, lift and fraudulent amount capture state their population and budget. Brier score and calibration charts concern the score's relationship to observed synthetic labels; a score is not a verified probability of real fraud.

Bootstrap intervals resample customer clusters where identifiers exist. The experiments use 150 replicates; an optional UI recalculation uses 100, with explicit seeds. These intervals address sampling variability within the simulation. They do not quantify the gap between synthetic and real data. Small cohorts and cohorts without both classes are identified instead of receiving invented discrimination scores.

PSI uses training-derived quantile bins and exposes sample sizes. It is descriptive simulated drift; the dashboard does not claim real-time production drift monitoring. Subgroup metrics show denominators. SHAP explains the frozen reference model's output, while research importance is labelled separately as candidate feature importance.

## Reproducibility and promotion

Install the exact development lock, use Python 3.12, single-threaded numerical environment variables and the recorded seed. Download analytical assets from the manifest or rebuild with `scripts/build_research_assets.py --rebuild`; hashes must match before release publication. Existing releases are never clobbered. A new scientific result requires a new reviewed manifest, rather than adjusting hashes to hide a mismatch.

The inference API continues serving model v1.0.0. Promotion requires a separately reviewed artifact contract, comparable validation, stability/calibration checks and a rollback plan. The stronger method, additional evidence and visible negative findings are the current deliverables; automatic improvement from larger synthetic data is not claimed.
