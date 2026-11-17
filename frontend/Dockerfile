FROM python:3.12-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:/app/src ARTIFACTS_ROOT=/app/artifacts \
    PIP_NO_CACHE_DIR=1 APP_ENV=production \
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
WORKDIR /app
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false FRAUD_INFERENCE_MODE=embedded
COPY requirements/demo.lock ./requirements/demo.lock
RUN python -m pip install --require-hashes -r requirements/demo.lock \
    && useradd --create-home --uid 10001 app
COPY .streamlit ./.streamlit
COPY frontend ./frontend
COPY api ./api
COPY src ./src
COPY configs ./configs
COPY data/interim/claims.parquet ./data/interim/claims.parquet
COPY data/interim/policies.parquet ./data/interim/policies.parquet
COPY artifacts/metadata ./artifacts/metadata
COPY artifacts/models ./artifacts/models
COPY artifacts/preprocessors ./artifacts/preprocessors
COPY artifacts/explainability ./artifacts/explainability
COPY artifacts/predictions/claim_scores.parquet ./artifacts/predictions/claim_scores.parquet
COPY artifacts/research ./artifacts/research
COPY scripts/fetch_research_assets.py ./scripts/fetch_research_assets.py
COPY scripts/serve_demo.py ./scripts/serve_demo.py
RUN python scripts/fetch_research_assets.py
USER app
EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:'+os.getenv('PORT','8501')+'/_stcore/health',timeout=3)" || exit 1
CMD ["python", "scripts/serve_demo.py"]
