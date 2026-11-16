This release distributes **synthetic data only** for the project's Data Science Lab.
The versioned manifest `configs/research-assets.json` records exact byte sizes and
SHA-256 hashes. Downloads are verified before loading. Existing assets are never
overwritten by the publishing workflow.

The reference corpus and published inference model remain separate from the
expanded longitudinal experiment. Candidate predictions cover held-out dates only.
The reports record the temporal split, seed, preprocessing comparisons, selection
rule and limitations. No performance on real insurance data is claimed.

Reproduce the reviewed assets with `python scripts/build_research_assets.py --rebuild`
after installing `requirements/dev.lock`. Fetch them with
`python scripts/fetch_research_assets.py` for exploration without retraining.
